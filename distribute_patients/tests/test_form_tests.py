from django import forms
from django.test import TestCase
from django.utils import timezone

from ..forms import PatientCountForm, PatientDesignateForm, BasePatientDesignateFormSet, SetRounderForm, \
    CurrentRounderForm, BaseRounderFormSet
from ..helper_fxns import helper_fxn_create_distribution_with_4_sample_line_items
from ..models import Distribution, Patient, Provider, PatientAssignmentLineItem


class SetRounderFormTests(TestCase):
    def test_can_create_form(self):
        form = SetRounderForm()
        self.assertIsInstance(form, SetRounderForm)

    def test_saving_form_creates_provider(self):
        self.assertEqual(Provider.objects.count(), 0)
        data = {'abbreviation': 'JLoh', 'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_provider_field_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'abbreviation': '', 'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(Provider.objects.count(), 0)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_starting_total_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'abbreviation': 'provA', 'starting_total': '', 'starting_CCU': 3, 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(Provider.objects.count(), 0)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_starting_CCU_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'abbreviation': 'provA', 'starting_total': 8, 'starting_CCU': '', 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(Provider.objects.count(), 0)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_starting_COVID_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'abbreviation': 'provA', 'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': ''}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(Provider.objects.count(), 0)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_an_existing_abbreviation_in_db_does_not_create_a_new_provider_or_line_item(self):
        self.assertEqual(Provider.objects.count(), 0)
        data = {'abbreviation': 'JLoh', 'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'abbreviation': 'JLoh', 'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = SetRounderForm(data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)


class CurrentRounderFormTests(TestCase):
    def test_can_create_form_given_provider(self):
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'))
        self.assertIsInstance(form, CurrentRounderForm)

    def test_saving_form_given_provider_does_not_create_new_provider(self):
        self.assertEqual(Provider.objects.count(), 0)
        data = {'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'), data=data)
        self.assertEqual(Provider.objects.count(), 1)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_given_provider_and_valid_numbers_is_valid_but_does_not_create_new_line_item(self):
        self.assertEqual(Provider.objects.count(), 0)
        data = {'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': 2}
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'), data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)


    def test_saving_form_with_blank_starting_total_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'starting_total': '', 'starting_CCU': 3, 'starting_COVID': 2}
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'), data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_starting_CCU_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'starting_total': 8, 'starting_CCU': '', 'starting_COVID': 2}
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'), data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)

    def test_saving_form_with_blank_starting_COVID_is_valid_but_does_not_create_line_item(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        data = {'starting_total': 8, 'starting_CCU': 3, 'starting_COVID': ''}
        form = CurrentRounderForm(provider=Provider.objects.create(abbreviation='provA'), data=data)
        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)



class RounderFormSetWithSetRounderFormTests(TestCase):
    def test_can_create_formset(self):
        RounderFormSet = forms.formset_factory(form=SetRounderForm, formset=BaseRounderFormSet)
        formset = RounderFormSet()
        self.assertIsInstance(formset, RounderFormSet)

    def test_newly_created_formset_forms_include_form_id_as_hidden_field(self):
        RounderFormSet = forms.formset_factory(form=SetRounderForm, formset=BaseRounderFormSet)
        formset = RounderFormSet()
        self.assertEqual(len(formset.forms), 12)
        for index, form in enumerate(formset.forms):
            self.assertEqual(form.id, index + 1)

    def test_saving_formset_creates_new_distribution(self):
        data = {'form-TOTAL_FORMS': 12, 'form-INITIAL_FORMS': 12}
        provider_names = ['provA', 'provB', 'provC', 'provD', 'provE', 'provF', 'provG', 'provH']
        starting_totals = [11, 12, 14, 15, 9, 8, 16, 13]
        starting_CCUs = [2, 5, 3, 7, 0, 1, 1, 0]
        starting_COVIDs = [1, 2, 5, 0, 3, 6, 4, 3]
        for i in range(12):
            data.update({f'form-{i}-id': i + 1})
            try:
                provider_name = provider_names[i]
            except IndexError:
                provider_name = ''
            try:
                starting_total = starting_totals[i]
            except IndexError:
                starting_total = ''
            try:
                starting_CCU = starting_CCUs[i]
            except IndexError:
                starting_CCU = ''
            try:
                starting_COVID = starting_COVIDs[i]
            except IndexError:
                starting_COVID = ''
            data.update({f'form-{i}-abbreviation': provider_name})
            data.update({f'form-{i}-starting_total': starting_total})
            data.update({f'form-{i}-starting_CCU': starting_CCU})
            data.update({f'form-{i}-starting_COVID': starting_COVID})
        RounderFormSet = forms.formset_factory(form=SetRounderForm, formset=BaseRounderFormSet)
        formset = RounderFormSet(data=data)
        formset.full_clean()
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(Distribution.objects.count(), 1)

    def test_saving_formset_creates_new_instances_of_line_items_for_non_blank_provider_abbrevs(self):
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        provider_names = provider_names = ['provA', 'provB', 'provC', 'provD', 'provE', 'provF', 'provG', 'provH']
        data = {'form-TOTAL_FORMS': 12, 'form-INITIAL_FORMS': 12}
        provider_names = ['provA', 'provB', 'provC', 'provD', 'provE', 'provF', 'provG', 'provH']
        starting_totals = [11, 12, 14, 15, 9, 8, 16, 13]
        starting_CCUs = [2, 5, 3, 7, 0, 1, 1, 0]
        starting_COVIDs = [1, 2, 5, 0, 3, 6, 4, 3]
        for i in range(12):
            data.update({f'form-{i}-id': i + 1})
            try:
                provider_name = provider_names[i]
            except IndexError:
                provider_name = ''
            try:
                starting_total = starting_totals[i]
            except IndexError:
                starting_total = ''
            try:
                starting_CCU = starting_CCUs[i]
            except IndexError:
                starting_CCU = ''
            try:
                starting_COVID = starting_COVIDs[i]
            except IndexError:
                starting_COVID = ''
            data.update({f'form-{i}-abbreviation': provider_name})
            data.update({f'form-{i}-starting_total': starting_total})
            data.update({f'form-{i}-starting_CCU': starting_CCU})
            data.update({f'form-{i}-starting_COVID': starting_COVID})
        RounderFormSet = forms.formset_factory(form=SetRounderForm, formset=BaseRounderFormSet)
        formset = RounderFormSet(data=data)
        formset.full_clean()
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 8)
        for line_item in PatientAssignmentLineItem.objects.all():
            self.assertEqual(line_item.distribution, Distribution.objects.first())

    def test_saving_formset_with_same_data_in_two_forms_creates_only_one_line_item(self):
        # same as prior, but provider name is duplicated, anticipate will make one fewer line item
        data = {'form-TOTAL_FORMS': 12, 'form-INITIAL_FORMS': 12}
        provider_names = ['provA', 'provB', 'provC', 'provD', 'provE', 'provF', 'provG', 'provG']
        starting_totals = [11, 12, 14, 15, 9, 8, 16, 13]
        starting_CCUs = [2, 5, 3, 7, 0, 1, 1, 0]
        starting_COVIDs = [1, 2, 5, 0, 3, 6, 4, 3]
        for i in range(12):
            data.update({f'form-{i}-id': i + 1})
            try:
                provider_name = provider_names[i]
            except IndexError:
                provider_name = ''
            try:
                starting_total = starting_totals[i]
            except IndexError:
                starting_total = ''
            try:
                starting_CCU = starting_CCUs[i]
            except IndexError:
                starting_CCU = ''
            try:
                starting_COVID = starting_COVIDs[i]
            except IndexError:
                starting_COVID = ''
            data.update({f'form-{i}-abbreviation': provider_name})
            data.update({f'form-{i}-starting_total': starting_total})
            data.update({f'form-{i}-starting_CCU': starting_CCU})
            data.update({f'form-{i}-starting_COVID': starting_COVID})
        RounderFormSet = forms.formset_factory(form=SetRounderForm, formset=BaseRounderFormSet)
        formset = RounderFormSet(data=data)
        formset.full_clean()
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 7)
        for line_item in PatientAssignmentLineItem.objects.all():
            self.assertEqual(line_item.distribution, Distribution.objects.first())


class PatientCountFormTests(TestCase):
    def test_can_create_form(self):
        form = PatientCountForm()
        self.assertIsInstance(form, PatientCountForm)

    def test_saving_form_creates_distribution(self):
        self.assertEqual(Distribution.objects.count(), 0)
        data = {'count_to_distribute': 14}
        form = PatientCountForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(Distribution.objects.first().count_to_distribute, 14)


class PatientDesignateFormTests(TestCase):
    def test_can_create_form(self):
        form = PatientDesignateForm()
        self.assertIsInstance(form, PatientDesignateForm)

    def test_saving_form_creates_patient(self):
        Distribution.objects.create()  # as it stands, any new patient is automatically assigned to last distribution
        self.assertEqual(Patient.objects.count(), 0)
        form = PatientDesignateForm(data={'CCU': True, 'COVID': True, 'number_designation': 1})
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Patient.objects.count(), 1)
        patient = Patient.objects.first()
        self.assertEqual(patient.CCU, True)
        self.assertEqual(patient.COVID, True)
        self.assertEqual(patient.bounce_to, None)


class PatientDesignateFormSetTests(TestCase):
    def test_can_create_formset(self):
        Distribution.objects.create()
        PatientDesignateFormSet = forms.modelformset_factory(model=Patient,
                                                             fields=['CCU', 'COVID',
                                                                     'bounce_to'],
                                                             formset=BasePatientDesignateFormSet)
        formset = PatientDesignateFormSet(distribution_id=1)
        self.assertIsInstance(formset, PatientDesignateFormSet)

    def test_newly_created_formset_forms_have_instances_of_patients_from_the_given_distribution(self):
        distribution = Distribution.objects.create()
        PatientDesignateFormSet = forms.modelformset_factory(model=Patient,
                                                             fields=['CCU', 'COVID',
                                                                     'bounce_to'],
                                                             formset=BasePatientDesignateFormSet)
        formset = PatientDesignateFormSet(distribution_id=1)
        self.assertEqual(len(formset.forms), 0)
        for i in range(6):
            Patient.objects.create(distribution=distribution, number_designation=i + 1)
        formset = PatientDesignateFormSet(distribution_id=1)
        self.assertEqual(len(formset.forms), 6)

    def test_newly_created_formset_forms_have_bounceback_choices_from_current_distribution_providers(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        distribution = Distribution.objects.last()
        PatientDesignateFormSet = forms.modelformset_factory(model=Patient,
                                                             fields=['CCU', 'COVID',
                                                                     'bounce_to'],
                                                             formset=BasePatientDesignateFormSet)
        for i in range(6):
            Patient.objects.create(distribution=distribution, number_designation=i + 1)
        formset = PatientDesignateFormSet(distribution_id=1)
        for form in formset.forms:
            form.fields['bounce_to'].queryset = Provider.objects.filter(
                patientassignmentlineitem__in=distribution.get_ordered_line_items())

    def test_saving_formset_with_previously_created_patients_updates_the_patients(self):
        distribution = Distribution.objects.create()
        for i in range(4):
            Patient.objects.create(distribution=distribution, number_designation=i + 1)
        data = {
            'form-TOTAL_FORMS': 4,
            'form-INITIAL_FORMS': 4,
            'form-0-distribution': 1,
            'form-1-distribution': 1,
            'form-2-distribution': 1,
            'form-3-distribution': 1,
            'form-0-id': 1,
            'form-1-id': 2,
            'form-2-id': 3,
            'form-3-id': 4,
            'form-0-COVID': True,
            'form-3-CCU': True
        }
        PatientDesignateFormSet = forms.modelformset_factory(model=Patient,
                                                             fields=['CCU', 'COVID', 'bounce_to'],
                                                             formset=BasePatientDesignateFormSet)
        formset = PatientDesignateFormSet(distribution_id=distribution.id, data=data)
        formset.full_clean()
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(Patient.objects.count(), 4)
        for patient in Patient.objects.all():
            if patient.id == 1:
                self.assertEqual(patient.COVID, True)
            else:
                self.assertEqual(patient.COVID, False)
            if patient.id == 4:
                self.assertEqual(patient.CCU, True)
            else:
                self.assertEqual(patient.CCU, False)
