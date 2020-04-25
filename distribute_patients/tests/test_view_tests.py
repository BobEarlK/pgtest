from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from ..forms import PatientCountForm, PatientDesignateForm
from ..helper_fxns import helper_fxn_create_distribution_with_4_sample_line_items, \
    helper_fxn_create_motley_list_of_patients_assign_to_distribution
from ..models import Distribution, Patient, Provider, PatientAssignmentLineItem


class SetRoundersTests(TestCase):
    def test_view_resolves_url(self):
        url = '/set_rounders/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'distribute:set_rounders')

    def test_view_gets_success_status_code(self):
        url = reverse('distribute:set_rounders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('distribute:set_rounders')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'distribute_patients/set_rounders.html')

    def test_view_context_contains_rounder_formset(self):
        url = reverse('distribute:set_rounders')
        response = self.client.get(url)
        self.assertEqual(len(response.context['rounder_formset']), 12)

    def test_posting_data_to_view_creates_line_items_assigned_to_a_new_distribution(self):
        url = reverse('distribute:set_rounders')
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
        self.assertEqual(Distribution.objects.count(), 0)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 0)
        self.client.post(url, data=data)
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 8)
        for line_item in PatientAssignmentLineItem.objects.all():
            self.assertEqual(line_item.distribution, Distribution.objects.first())

    def test_posting_data_to_view_redirects_to_edit_count_view(self):
        url = reverse('distribute:set_rounders')
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
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('distribute:edit_count'))


class CurrentRoundersTests(TestCase):
    def test_view_resolves_url(self):
        url = '/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'distribute:current_rounders')

    def test_view_redirects_to_set_rounders_if_no_distribution(self):
        url = reverse('distribute:current_rounders')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('distribute:set_rounders'))

    def test_view_gets_success_status_code(self):
        # all tests of current_rounders view have to have a distribution
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:current_rounders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:current_rounders')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'distribute_patients/current_rounders.html')

    def test_view_context_contains_rounder_formset(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:current_rounders')
        response = self.client.get(url)
        self.assertEqual(len(response.context['current_rounder_formset']), 12)

    def test_posting_data_to_view_creates_line_items_assigned_to_a_new_distribution(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:current_rounders')
        data = {'form-TOTAL_FORMS': 12, 'form-INITIAL_FORMS': 12}
        starting_totals = [14, 16, 12, 10, 8, 6, 10, 12]
        starting_CCUs = [1, 3, 2, 0, 0, 3, 1, 0]
        starting_COVIDs = [2, 2, 5, 0, 1, 3, 2, 0]
        for i in range(12):
            data.update({f'form-{i}-id': i + 1})
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
            data.update({f'form-{i}-starting_total': starting_total})
            data.update({f'form-{i}-starting_CCU': starting_CCU})
            data.update({f'form-{i}-starting_COVID': starting_COVID})
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 8)
        self.client.post(url, data=data)
        self.assertEqual(Distribution.objects.count(), 2)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 16)
        distribution = Distribution.objects.last()
        for index, line_item in enumerate(distribution.line_items.all()):
            self.assertEqual(line_item.starting_census.total, starting_totals[index])
            self.assertEqual(line_item.starting_census.CCU, starting_CCU[index])
            self.assertEqual(line_item.starting_census.COVID, starting_COVID[index])

    def test_posting_data_to_view_redirects_to_edit_count_view(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:current_rounders')
        data = {'form-TOTAL_FORMS': 12, 'form-INITIAL_FORMS': 12}
        starting_totals = [14, 16, 12, 10, 8, 6, 10, 12]
        starting_CCUs = [1, 3, 2, 0, 0, 3, 1, 0]
        starting_COVIDs = [2, 2, 5, 0, 1, 3, 2, 0]
        for i in range(12):
            data.update({f'form-{i}-id': i + 1})
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
            data.update({f'form-{i}-starting_total': starting_total})
            data.update({f'form-{i}-starting_CCU': starting_CCU})
            data.update({f'form-{i}-starting_COVID': starting_COVID})
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(PatientAssignmentLineItem.objects.count(), 8)
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('distribute:edit_count'))

    def test_view_content_contains_link_to_modify_providers_page(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        self.fail('Finish the test')

    def test_view_content_contains_link_to_set_rounders_page(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        self.fail('Finish the test')


class EditCountToDistributeTests(TestCase):
    def test_view_resolves_url(self):
        url = f'/distribute/edit_count/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'distribute:edit_count')

    def test_view_gets_success_status_code(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:edit_count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:edit_count')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'distribute_patients/edit_count.html')

    def test_view_context_contains_patient_count_form(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:edit_count')
        response = self.client.get(url)
        self.assertIsInstance(response.context['patient_count_form'], PatientCountForm)

    def test_posting_count_to_submit_count_redirects_to_designate_patients_view(self):
        url = reverse('distribute:edit_count')
        response = self.client.post(url, data={'count_to_distribute': 5}, follow=True)
        self.assertRedirects(response, reverse('distribute:designate_patients'))

    def test_posting_count_to_edit_count_view_instantiates_distribution_and_patients(self):
        url = reverse('distribute:edit_count')
        response = self.client.post(url, data={'count_to_distribute': 13})
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(Patient.objects.count(), 13)
        for index, patient in enumerate(Patient.objects.all()):
            self.assertEqual(patient.distribution, Distribution.objects.first())
            self.assertEqual(patient.number_designation, index + 1)

    def test_posting_count_to_edit_count_view_creates_no_line_items_if_no_prior_distribution(self):
        url = reverse('distribute:edit_count')
        response = self.client.post(url, data={'count_to_distribute': 13})
        self.assertEqual(Distribution.objects.count(), 1)
        self.assertEqual(Distribution.objects.last().line_items.count(), 0)


class DesignatePatientsViewTests(TestCase):

    def setUp(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        distribution = Distribution.objects.last()
        for i in range(4):
            Patient.objects.create(distribution=distribution, number_designation=i + 1)

    def test_view_resolves_url(self):
        url = f'/distribute/designate_patients/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'distribute:designate_patients')

    def test_view_gets_success_status_code(self):
        url = reverse('distribute:designate_patients')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('distribute:designate_patients')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'distribute_patients/designate_patients.html')

    def test_view_context_contains_patient_count_form(self):
        url = reverse('distribute:designate_patients')
        response = self.client.get(url)
        self.assertEqual(len(response.context['formset']), 4)
        for form in response.context['formset']:
            self.assertIsInstance(form.instance, Patient)

    def test_view_context_contains_ordered_providers_with_starting_censuses(self):
        self.distribution = Distribution.objects.first()
        abbreviations = ['provA', 'provB', 'provC', 'provD']
        totals = [10, 11, 13, 11]
        CCUs = [2, 3, 2, 1]
        COVIDs = [0, 3, 1, 2]
        orders = [3, 1, 2, 4]
        # for i in range(4):
        #     provider = Provider.objects.get_or_create(abbreviation=abbreviations[i])[0]
        #     starting_total = totals[i]
        #     starting_CCU = CCUs[i]
        #     starting_COVID = COVIDs[i]
        #     order = orders[i]
        #     PatientAssignmentLineItem.objects.create_line_item(distribution=self.distribution,
        #                                                        provider=provider,
        #                                                        starting_total=starting_total,
        #                                                        starting_CCU=starting_CCU,
        #                                                        starting_COVID=starting_COVID,
        #                                                        position_in_batting_order=order)
        url = reverse('distribute:designate_patients')
        response = self.client.get(url)
        self.assertEqual(response.context['ordered_line_items'].count(), 4)
        for index, line_item in enumerate(response.context['ordered_line_items']):
            if index == 0:
                self.assertEqual(line_item.id, 2)
                self.assertEqual(line_item.provider.abbreviation, 'provB')
                self.assertEqual(line_item.starting_census.total, 11)
                self.assertEqual(line_item.starting_census.CCU, 3)
                self.assertEqual(line_item.starting_census.COVID, 3)
            elif index == 1:
                if index == 1:
                    self.assertEqual(line_item.id, 3)
                    self.assertEqual(line_item.provider.abbreviation, 'provC')
                    self.assertEqual(line_item.starting_census.total, 13)
                    self.assertEqual(line_item.starting_census.CCU, 2)
                    self.assertEqual(line_item.starting_census.COVID, 1)
            elif index == 2:
                if index == 2:
                    self.assertEqual(line_item.id, 1)
                    self.assertEqual(line_item.provider.abbreviation, 'provA')
                    self.assertEqual(line_item.starting_census.total, 10)
                    self.assertEqual(line_item.starting_census.CCU, 2)
                    self.assertEqual(line_item.starting_census.COVID, 0)
            elif index == 3:
                if index == 2:
                    self.assertEqual(line_item.id, 4)
                    self.assertEqual(line_item.provider.abbreviation, 'provD')
                    self.assertEqual(line_item.starting_census.total, 11)
                    self.assertEqual(line_item.starting_census.CCU, 1)
                    self.assertEqual(line_item.starting_census.COVID, 0)

    def test_posting_data_to_view_updates_patient_characteristics(self):
        url = reverse('distribute:designate_patients')
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
        self.client.post(url, data=data)
        self.assertEqual(Patient.objects.count(), 4)
        for i in range(4):
            patient = Patient.objects.all()[i]
            if i == 0:
                self.assertTrue(patient.COVID)
                self.assertFalse(patient.CCU)
            elif i == 3:
                self.assertTrue(patient.CCU)
                self.assertFalse(patient.COVID)
            else:
                self.assertFalse(patient.COVID)
                self.assertFalse(patient.CCU)

    def test_posting_data_to_view_redirects_to_patient_assignments_view(self):
        url = reverse('distribute:designate_patients')
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
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('distribute:patient_assignments'))

    def test_posting_data_to_view_assigns_patients_to_line_items(self):
        url = reverse('distribute:designate_patients')
        distribution = Distribution.objects.last()
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
        for line_item in distribution.get_ordered_line_items():
            self.assertEqual(line_item.assigned_patients.count(), 0)
        response = self.client.post(url, data=data)
        self.assertEqual(Patient.objects.count(), 4)
        for patient in Patient.objects.all():
            self.assertIsNotNone(patient.patient_assignment_line_item)
        self.assertRedirects(response, reverse('distribute:patient_assignments'))


class PatientAssignmentsViewTests(TestCase):
    def test_view_resolves_url(self):
        url = f'/distribute/patient_assignments/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'distribute:patient_assignments')

    def test_view_gets_success_status_code(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:patient_assignments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:patient_assignments')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'distribute_patients/patient_assignments.html')

    def test_view_context_contains_ordered_line_items(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('distribute:patient_assignments')
        response = self.client.get(url)
        self.assertEqual(response.context['ordered_line_items'].count(), 4)

    def test_view_context_contains_assigned_nonbounceback_patient_list(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        distribution = Distribution.objects.last()
        helper_fxn_create_motley_list_of_patients_assign_to_distribution(patient_count=20, distribution=distribution)
        distribution.assign_all_patients()
        url = reverse('distribute:patient_assignments')
        response = self.client.get(url)
        self.assertEqual(len(response.context['patient_assignment_dict']), 4)


class COVIDLinksView(TestCase):
    def test_view_resolves_url(self):
        url = f'/covid_links/'
        view = resolve(url)
        self.assertEqual(view.view_name, 'covid_links')

    def test_view_gets_success_status_code(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('covid_links')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        helper_fxn_create_distribution_with_4_sample_line_items()
        url = reverse('covid_links')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'covid_links.html')
