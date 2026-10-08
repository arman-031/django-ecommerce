from django import forms


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, label='تعداد')
    color = forms.ChoiceField(required=False, label='رنگ')
    size = forms.ChoiceField(required=False, label='سایز')

    def __init__(self, *args, product, **kwargs):
        super().__init__(*args, **kwargs)
        for field, relation in [('color', product.color), ('size', product.size)]:
            choices = [(title, title) for title in relation.values_list('title', flat=True)]
            self.fields[field].choices = choices
            self.fields[field].required = bool(choices)
            self.fields[field].error_messages.update({
                'required': 'لطفاً یک گزینه انتخاب کنید.',
                'invalid_choice': 'گزینه انتخاب‌شده برای این محصول معتبر نیست.',
            })


class DiscountForm(forms.Form):
    discount_code = forms.CharField(max_length=10, label='کد تخفیف')
