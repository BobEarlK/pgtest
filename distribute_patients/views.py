from django import forms
from django.shortcuts import render, redirect, reverse
from django.views.generic.edit import CreateView
from django.utils import timezone

from .helper_fxns import date_str_to_date

from .forms import PatientCountForm, BasePatientDesignateFormSet, RounderForm, BaseRounderFormSet
from .models import Distribution, Patient, Provider


def set_rounders(request):
    RounderFormSet = forms.formset_factory(form=RounderForm, formset=BaseRounderFormSet)
    if request.method == 'POST':
        formset = RounderFormSet(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('distribute:edit_count'))
    else:
        rounder_formset = RounderFormSet()
        context = {'date': timezone.localdate(), 'rounder_formset': rounder_formset}
        return render(request, 'distribute_patients/set_rounders.html', context=context)


def edit_count_to_distribute(request):
    distribution = Distribution.objects.last()
    if request.method == 'POST':
        form = PatientCountForm(data=request.POST, instance=distribution)
        if form.is_valid():
            distribution = form.save()
            # distribution.add_duplicated_line_items_from_prior_distribution()
            for i in range(distribution.count_to_distribute):
                Patient.objects.create(distribution=distribution, number_designation=i + 1)
            # duplicates the providers, starting
            # census from previous distribution
            return redirect(reverse('distribute:designate_patients'))
    else:
        patient_count_form = PatientCountForm(instance=distribution)
        context = {'date': timezone.localdate(), 'ordered_line_items': distribution.get_ordered_line_items(),
                   'patient_count_form': patient_count_form}
        return render(request, 'distribute_patients/edit_count.html', context=context)


def designate_patients(request):
    distribution = Distribution.objects.last()
    PatientDesignateFormSet = forms.modelformset_factory(model=Patient,
                                                         fields=['CCU', 'COVID', 'bounce_to'],
                                                         formset=BasePatientDesignateFormSet)
    if request.method == 'POST':
        formset = PatientDesignateFormSet(distribution_id=distribution.id, data=request.POST)
        if formset.is_valid():
            formset.save()
            distribution.assign_all_patients()
        return redirect(reverse('distribute:patient_assignments'))
    else:
        formset = PatientDesignateFormSet(distribution_id=distribution.id)
        context = {'date': timezone.localdate(), 'ordered_line_items': distribution.get_ordered_line_items(),
                   'formset': formset}
        return render(request, 'distribute_patients/designate_patients.html', context=context)


def patient_assignments(request):
    distribution = Distribution.objects.last()
    patient_assignment_dict = {}
    for line_item in distribution.get_ordered_line_items():
        assigned_patient_dict = {}
        bounceback_pts = line_item.assigned_patients.filter(bounce_to__isnull=False)
        dual_pos_pts = line_item.assigned_patients.filter(bounce_to__isnull=True, COVID=True, CCU=True)
        ccu_pos_pts = line_item.assigned_patients.filter(bounce_to__isnull=True, COVID=False, CCU=True)
        covid_pos_pts = line_item.assigned_patients.filter(bounce_to__isnull=True, COVID=True, CCU=False)
        dual_neg_pts = line_item.assigned_patients.filter(bounce_to__isnull=True, COVID=False, CCU=False)
        assigned_patient_dict.update(
            {'bounceback_pts': bounceback_pts, 'dual_pos_pts': dual_pos_pts, 'ccu_pos_pts': ccu_pos_pts,
             'covid_pos_pts': covid_pos_pts, 'dual_neg_pts': dual_neg_pts})
        patient_assignment_dict.update(
            {line_item: assigned_patient_dict})
    context = {'date': timezone.localdate(), 'ordered_line_items': distribution.get_ordered_line_items(),
               'patient_assignment_dict': patient_assignment_dict}
    return render(request, 'distribute_patients/patient_assignments.html', context=context)


def covid_links(request):
    links = {
        "Evergreen 'Lessons Learned'": 'http://www.evergreenhealth.com/covid-19-lessons',
        'Evergreen COVID-19 public resources': 'https://www.evergreenhealth.com/coronavirus',
        'Evergreen Health COVID-19 Daily Patient Update': 'https://evergreenhealth.us14.list-manage.com/track/click?u=5da20b2b88e84f496fd6c97d0&id=dff97c6cd6&e=4771d6f5ea',
        'Healthdata COVID-19 Projections':'https://evergreenhealth.us14.list-manage.com/track/click?u=5da20b2b88e84f496fd6c97d0&id=48770d03a4&e=4771d6f5ea',
        'CDC Guidance for COVID-19 patient discharges':'https://www.cdc.gov/coronavirus/2019-ncov/hcp/disposition-hospitalized-patients.html',
        'Surviving Sepsis COVID-19 Guidelines':'https://www.sccm.org/getattachment/Disaster/SSC-COVID19-Critical-Care-Guidelines.pdf',
        'Fighting COVID technology center': 'https://www.alibabacloud.com/covid-19-global-medixchange',
        'PPE Donning/Doffing Video': 'https://youtu.be/twE8UtwndeQ',
        'BlueJeans App Workflow': 'http://employees.evergreenhealth.com/IT/Projects/covid19/Project%20Documents/Design-Build-Test/COVID-19%20Virtual%20Visits/Communication/Patient%20to%20Family%20Virtual%20Visit/CCU%20%20Patient%20to%20Family%20Workflow.pdf?Web=1',
        'Microsoft Teams Getting Started - Installation': 'http://employees.evergreenhealth.com/IT/Projects/covid19/Project%20Documents/Design-Build-Test/COVID-19%20Virtual%20Visits/Communication/MS%20Teams/Teams%20-Getting%20Started-Installation.docx',
        'Microsoft Teams Usage Tips': 'http://employees.evergreenhealth.com/IT/Projects/covid19/Project%20Documents/Design-Build-Test/COVID-19%20Virtual%20Visits/Communication/MS%20Teams/MS%20Teams%20Usage%20Tips.docx',

    }
    return render(request, 'covid_links.html', context={'links': links})
