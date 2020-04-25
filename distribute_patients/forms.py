from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from django import forms
from django.urls import reverse
from django.utils import timezone

from .models import Distribution, Patient, Provider, PatientAssignmentLineItem, OptimalCensus, StartingCensus, \
    AssignedCensus


class BaseRounderForm(forms.Form):
    id = forms.IntegerField(required=False)
    starting_total = forms.IntegerField(max_value=40, min_value=0, required=False)
    starting_CCU = forms.IntegerField(max_value=40, min_value=0, required=False)
    starting_COVID = forms.IntegerField(max_value=40, min_value=0, required=False)

    def save(self, provider, *args, **kwargs):
        if type(self.cleaned_data['starting_total']) == int and \
                type(self.cleaned_data['starting_CCU']) == int and \
                type(self.cleaned_data['starting_COVID']) == int:
            starting_census = StartingCensus.objects.create(total=self.cleaned_data['starting_total'],
                                                            CCU=self.cleaned_data[
                                                                'starting_CCU'],
                                                            COVID=self.cleaned_data['starting_COVID'])
            return PatientAssignmentLineItem(provider=provider, starting_census=starting_census)
        else:
            return None


class SetRounderForm(BaseRounderForm):
    abbreviation = forms.CharField(max_length=6, required=False)

    def save(self, *args, **kwargs):
        if self.cleaned_data['abbreviation']:
            provider = Provider.objects.get_or_create(abbreviation=self.cleaned_data['abbreviation'])[0]
            return super().save(provider=provider, *args, **kwargs)
        else:
            return None

class CurrentRounderForm(BaseRounderForm):
    def __init__(self, provider, *args, **kwargs):
        self.provider = provider
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(provider=self.provider, *args, **kwargs)


class BaseRounderFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.extra = 12
        super().__init__(*args, **kwargs)
        for index, form in enumerate(self.forms):
            form.id = index + 1
            form.helper = FormHelper()
            form.helper.form_id = 'id_rounder_form'  # apparently don't show up when no form tag
            form.helper.form_class = 'dummy-form-class'
            form.helper.form_tag = False
            form.helper.disable_csrf = True
            form.helper.form_show_labels = False
            form.helper.layout = Layout(
                Div(
                    Field('id', type='hidden', value=form.id),  # hidden id field to add form id to POST data
                    Field('abbreviation', id='id_rounder_abbreviation_field', placeholder=f'rounder {form.id}',
                          wrapper_class='abbreviation-input col-3'),
                    Field('starting_total', id='id_starting_total_field', placeholder='total', wrapper_class='col-2'),
                    Field('starting_CCU', id='id_starting_CCU_field', placeholder='CCU', wrapper_class='col-2'),
                    Field('starting_COVID', id='id_starting_COVID_field', placeholder='COVID', wrapper_class='col-2'),
                    id='id_rounder_form', css_class='row dummy-class'),
            )

    def save(self, *args, **kwargs):
        distribution = Distribution.objects.create()
        for index, form in enumerate(self.forms):
            if form.is_valid():
                line_item = form.save()
                if line_item and not distribution.line_items.filter(
                        provider__abbreviation=line_item.provider.abbreviation):
                    line_item.distribution = distribution
                    line_item.position_in_batting_order = index + 1
                    optimal_census = OptimalCensus.objects.create(total=line_item.starting_census.total,
                                                                  CCU=line_item.starting_census.CCU,
                                                                  COVID=line_item.starting_census.COVID)
                    line_item.optimal_census = optimal_census
                    assigned_census = AssignedCensus.objects.create(total=line_item.starting_census.total,
                                                                    CCU=line_item.starting_census.CCU,
                                                                    COVID=line_item.starting_census.COVID)
                    line_item.assigned_census = assigned_census
                    line_item.save()


class PatientCountForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['count_to_distribute']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id_patient_count_to_distribute_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('distribute:edit_count')
        self.helper.add_input(Submit('submit', 'Submit'))


class PatientDesignateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['number_designation', 'CCU', 'COVID', 'bounce_to']

    def save(self, *args, **kwargs):
        patient = super().save(commit=False)
        patient.distribution = Distribution.objects.last()  # automatically assigns pt to last distribution
        patient.save()


class BasePatientDesignateFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        distribution = Distribution.objects.get(id=kwargs.pop('distribution_id'))
        self.extra = 0
        super().__init__(*args, **kwargs)
        self.queryset = distribution.patient_set.all()
        for index, form in enumerate(self.forms):
            form.fields['bounce_to'].queryset = Provider.objects.filter(
                patientassignmentlineitem__in=distribution.get_ordered_line_items())
            form.helper = FormHelper()
            form.helper.form_id = 'id_designate_patient_form'
            form.helper.form_class = 'dummy-form-class'
            form.helper.form_tag = False
            form.helper.disable_csrf = True
            form.helper.layout = Layout(
                Div(
                    Field('id', type='hidden', value=form.instance.id),  # hidden id field to add id to POST data
                    Field('CCU', wrapper_class='CCU-checkbox'),
                    css_class='form-row'),
                Div(
                    Field('COVID', wrapper_class='COVID-checkbox'),
                    css_class='form-row'),
                Div(
                    Field('bounce_to', wrapper_class='bounceback-dropdown'),
                    css_class='form-row'),

            )
