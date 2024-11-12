from django.shortcuts import render
from django.views.generic import ListView
from typing import Any
from .models import Voter
from .forms import VoterFilterForm 
from django.views.generic import DetailView
import plotly ## NEW
import plotly.graph_objects as go ## NEW

# Create your views here.

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])
            
            min_year = form.cleaned_data.get('min_year_of_birth')
            max_year = form.cleaned_data.get('max_year_of_birth')
        
            if min_year is not None:
                queryset = queryset.filter(date_of_birth__year__gte=min_year)
            if max_year is not None:
                queryset = queryset.filter(date_of_birth__year__lte=max_year)
            
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            if form.cleaned_data['v20state']:
                queryset = queryset.filter(v20state=form.cleaned_data['v20state'])
            if form.cleaned_data['v21town']:
                queryset = queryset.filter(v21town=form.cleaned_data['v21town'])
            if form.cleaned_data['v21primary']:
                queryset = queryset.filter(v21primary=form.cleaned_data['v21primary'])
            if form.cleaned_data['v22general']:
                queryset = queryset.filter(v22general=form.cleaned_data['v22general'])
            if form.cleaned_data['v23town']:
                queryset = queryset.filter(v23town=form.cleaned_data['v23town'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = VoterFilterForm(self.request.GET or None)
        return context
    
class VoterGraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])
        
            min_year = form.cleaned_data.get('min_year_of_birth')
            max_year = form.cleaned_data.get('max_year_of_birth')
        
            if min_year is not None:
                queryset = queryset.filter(date_of_birth__year__gte=min_year)
            if max_year is not None:
                queryset = queryset.filter(date_of_birth__year__lte=max_year)
        
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            if form.cleaned_data['v20state']:
                queryset = queryset.filter(v20state=form.cleaned_data['v20state'])
            if form.cleaned_data['v21town']:
                queryset = queryset.filter(v21town=form.cleaned_data['v21town'])
            if form.cleaned_data['v21primary']:
                queryset = queryset.filter(v21primary=form.cleaned_data['v21primary'])
            if form.cleaned_data['v22general']:
                queryset = queryset.filter(v22general=form.cleaned_data['v22general'])
            if form.cleaned_data['v23town']:
                queryset = queryset.filter(v23town=form.cleaned_data['v23town'])
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add aggregate data graphs to the context."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Filter form
        context['filter_form'] = VoterFilterForm(self.request.GET or None)

        # Histogram of Birth Years
        birth_years = [date.year for date in queryset.values_list('date_of_birth', flat=True) if date]
        year_counts = {year: birth_years.count(year) for year in set(birth_years)}
        x_years, y_counts = zip(*sorted(year_counts.items()))
        
        fig = go.Bar(x=x_years, y=y_counts, name='Birth Year Distribution')
        birth_year_histogram = plotly.offline.plot({"data": [fig]}, auto_open=False, output_type="div")
        context['birth_year_histogram'] = birth_year_histogram

        # Pie Chart of Party Affiliation
        party_affiliations = list(queryset.values_list('party_affiliation', flat=True))
        party_counts = {party: party_affiliations.count(party) for party in set(party_affiliations)}
        labels, values = zip(*party_counts.items())

        fig = go.Pie(labels=labels, values=values, name='Party Affiliation Distribution')
        party_affiliation_pie = plotly.offline.plot({"data": [fig]}, auto_open=False, output_type="div")
        context['party_affiliation_pie'] = party_affiliation_pie

        # Histogram of Election Participation
        participation_counts = {
            '2020 State': queryset.filter(v20state=True).count(),
            '2021 Town': queryset.filter(v21town=True).count(),
            '2021 Primary': queryset.filter(v21primary=True).count(),
            '2022 General': queryset.filter(v22general=True).count(),
            '2023 Town': queryset.filter(v23town=True).count(),
        }
        x_participation, y_participation = zip(*participation_counts.items())

        fig = go.Bar(x=x_participation, y=y_participation, name='Election Participation')
        participation_histogram = plotly.offline.plot({"data": [fig]}, auto_open=False, output_type="div")
        context['participation_histogram'] = participation_histogram

        return context