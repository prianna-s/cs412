from django import forms
from .models import Voter

class VoterFilterForm(forms.Form):
    party_affiliation = forms.ChoiceField(choices=[('', 'Any')] + [(party, party) for party in Voter.objects.values_list('party_affiliation', flat=True).distinct()], required=False)
    min_year_of_birth = forms.IntegerField(
    widget=forms.Select(choices=[('', 'Any')] + [(year, year) for year in range(1920, 2023)]),
    required=False,
    label="Minimum Year of Birth"
    )
    max_year_of_birth = forms.IntegerField(
    widget=forms.Select(choices=[('', 'Any')] + [(year, year) for year in range(1920, 2023)]),
    required=False,
    label="Maximum Year of Birth"
    )
    voter_score = forms.ChoiceField(choices=[('', 'Any')] + [(score, score) for score in range(6)], required=False)
    v20state = forms.BooleanField(required=False)
    v21town = forms.BooleanField(required=False)
    v21primary = forms.BooleanField(required=False)
    v22general = forms.BooleanField(required=False)
    v23town = forms.BooleanField(required=False)
