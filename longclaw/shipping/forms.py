from django.forms import ModelChoiceField, ModelForm

from longclaw.configuration.models import Configuration
from longclaw.shipping.models import Address, Country


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ["name", "line_1", "line_2", "city", "postcode", "country"]

    def __init__(self, *args, **kwargs):
        site = kwargs.pop("site", None)
        super(AddressForm, self).__init__(*args, **kwargs)

        # Edit the country field to only contain
        # countries specified for shipping
        all_countries = True
        if site:
            settings = Configuration.for_site(site)
            all_countries = settings.default_shipping_enabled
        if all_countries:
            queryset = Country.objects.all()
        else:
            queryset = Country.objects.exclude(shippingrate=None)
        self.fields["country"] = ModelChoiceField(queryset)
