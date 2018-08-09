from django import forms


class SearchRequest(forms.Form):
    search_req = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'id': 'search',
            'placeholder': 'Search for...',
        }))
