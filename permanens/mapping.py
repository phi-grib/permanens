#! -*- coding: utf-8 -*-

# Description    permanens command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2024 Manuel Pastor
#
# This file is part of permanens
#
# permanens is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Permanens is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with permanens. If not, see <http://www.gnu.org/licenses/>.

mental_disorders = [
    "Schizophrenia and other non-organic psychosis",
    "Mood [affective] disorders",
    "Neurotic disorders",
    "Eating disorders",
    "Borderline personality disorder",
    "Other personality disorders",
    "Habit and impulse disorders",
    "Behavioural and emotional disorders with onset usually occurring in childhood and adolescence",
    "Mental retardation",
    "Mental disorder, not otherwise specified"
]

mental_disorders_label = [
    "Psychotic disorders",
    "Mood disorders",
    "Neurotic disorders",
    "Eating disorders",
    "Borderline personality disorder",
    "Other personality disorders",
    "Impulse-control disorders",
    "Childhood-onset disorders",
    "Intellectual disability",
    "Unspecified mental disorder"
]

substance_use = [
    "Substance use disorder - alcohol",
    "Substance use disorder - opioids",
    "Substance use disorder - sedatives or hypnotics",
    "Substance use disorder - cocaine",
    "Substance use disorder - other stimulants (including caffeine)",
    "Substance use disorder - cannabinoids",
    "Substance use disorder - hallucinogens",
    "Substance use disorder - other, unspecified, or multiple drugs or psychoactive substances",
    "Substance use disorder - tobacco"
]

substance_use_label = [
    "Alcohol",
    "Opioids",
    "Sedatives / hypnotics",
    "Cocaine",
    "Stimulants",
    "Cannabis",
    "Hallucinogens",
    "Polysubstance / unspecified",
    "Tobacco",
]

others = [
    "Epilepsy",
    "Intracranial injury",
    "Hemiplegia",
    "Asthma",
    "Chest pain on breathing",
    "Chronic hepatitis",
    "HIV/AIDS",
    "Homicide, assault",
    "Weight loss",
    "Hereditary and idiopathic neuropathy",
    "Disorders of autonomic nervous system (inc autonomic dysreflexia)"

]

others_label = [
    "Epilepsy",
    "Intracranial injury",
    "Hemiplegia / paralysis",
    "Asthma",
    "Chest pain (on breathing)",
    "Chronic hepatitis",
    "HIV / AIDS",
    "Homicide or assault",
    "Weight loss",
    "Hereditary and idiopathic neuropathy",
    "Disorders of autonomic nervous system (inc autonomic dysreflexia)"
]

ATC = [
    "antidepressants",
    "anxiolytic",
    "medication for mood instability",
    "anti-ADHD",
    "first generation antipsychotics",
    "anti-EPS",
    "analgesics (opioid or non-opioid)",
    "anti-vertigo",
    "addiction medicine",
]

ATC_label = [
    "Antidepressants",
    "Anxiolytics / sedatives",
    "Medication for mood instability",
    "ADHD medication",
    "Antipsychotics (first generation)",
    "Anti-EPS agents",
    "Analgesics (opioid / non-opioid)",
    "Anti-vertigo agents",
    "Addiction treatment medication"
]

def condition_to_label (predictors, lang = 'en'):

    imental_disorders = []
    isubstance_use = []
    iothers = []

    for j,ipred in enumerate(mental_disorders):
        if ipred in predictors:
            imental_disorders.append(mental_disorders_label[j])
    
    for j,ipred in enumerate(substance_use):
        if ipred in predictors:
            isubstance_use.append(substance_use_label[j])

    for j,ipred in enumerate(others):
        if ipred in predictors:
            iothers.append(others_label[j])

    for ipred in predictors:
        if ipred in mental_disorders or ipred in substance_use or ipred in others:
            continue
        print ('*************', ipred)

    return_list = []


    if len(imental_disorders) > 0:
        return_list.append ('Registered mental disorder diagnosis')
        return_list.append (imental_disorders)
    
    if len(isubstance_use) > 0:
        return_list.append ('Registered substance use disorder diagnosis')
        return_list.append (isubstance_use)

    if len(iothers) > 0:
        return_list.append ('Other registered conditions')
        return_list.append (iothers)

    return (return_list)

def label_to_condition (labels, lang = 'en'):
    predictors = []
    for ilabel in labels:
        if ilabel in mental_disorders_label:
            predictors.append(mental_disorders[mental_disorders_label.index(ilabel)])
        elif ilabel in substance_use_label:
            predictors.append(substance_use[substance_use_label.index(ilabel)])
        elif ilabel in others_label:
            predictors.append(others[others_label.index(ilabel)])

    return (predictors)

def atc_to_label (drugs, lang = 'en'):
    result = []
    for j,iatc in enumerate(ATC):
        if iatc in drugs:
            result.append(ATC_label[j])
    for iatc in drugs:
        if iatc not in ATC:
            print ('>>>>>>>>>>>>>>>', iatc)
    return result

def label_to_atc (labels, lang='en'):
    result = []
    for ilabel in labels:
        if ilabel in ATC_label:
            result.append(ATC[ATC_label.index(ilabel)])
    return result

