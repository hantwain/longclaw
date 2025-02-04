from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from longclaw.basket.utils import get_basket_items
from longclaw.checkout.forms import CheckoutForm
from longclaw.checkout.utils import create_order
from longclaw.orders.models import Order
from longclaw.shipping.forms import AddressForm


@require_GET
def checkout_success(request, pk):
    order = get_object_or_404(Order, id=pk)
    return render(request, "checkout/success.html", {"order": order})


class CheckoutView(TemplateView):
    template_name = "checkout/checkout.html"
    checkout_form = CheckoutForm
    shipping_address_form = AddressForm
    billing_address_form = AddressForm

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        items, _ = get_basket_items(self.request)
        total_price = sum(item.total() for item in items)
        site = getattr(self.request, "site", None)
        context["checkout_form"] = self.checkout_form(self.request.POST or None)
        context["shipping_form"] = self.shipping_address_form(
            self.request.POST or None, prefix="shipping", site=site
        )
        context["billing_form"] = self.billing_address_form(
            self.request.POST or None, prefix="billing", site=site
        )
        context["basket"] = items
        context["total_price"] = total_price
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        checkout_form = context["checkout_form"]
        shipping_form = context["shipping_form"]
        all_ok = checkout_form.is_valid() and shipping_form.is_valid()
        if all_ok:
            email = checkout_form.cleaned_data["email"]
            shipping_option = checkout_form.cleaned_data.get("shipping_option", None)
            shipping_address = shipping_form.save()

            if checkout_form.cleaned_data["different_billing_address"]:
                billing_form = context["billing_form"]
                all_ok = billing_form.is_valid()
                if all_ok:
                    billing_address = billing_form.save()
            else:
                billing_address = shipping_address

        if all_ok:
            order = create_order(
                email,
                request,
                shipping_address=shipping_address,
                billing_address=billing_address,
                shipping_option=shipping_option,
                capture_payment=True,
            )
            return HttpResponseRedirect(
                reverse("longclaw_checkout_success", kwargs={"pk": order.id})
            )
        return super(CheckoutView, self).render_to_response(context)
