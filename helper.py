"""
Helper functions for data transformation
"""

from itertools import chain
import pandas as pd

ROOT_FIELDS = ['safetyreportid', 'receivedate', 'occurcountry', 'serious']  # interested fields in the root node
PATIENT_FIELDS = ['patientsex', 'patientonsetage', 'patientonsetageunit']  # interested fields within the patient node
REACTION_FIELDS = ['reactionmeddrapt', 'reactionoutcome']  # interested fields within the patient.reaction node
DRUG_FIELDS = ['manufacturer_name',
               'product_type',
               'route',
               'generic_name',
               'brand_name',
               'substance_name']  # interested fields within the patient.drug.openfda node, note the values are all lists --> only extract the first one

def dict_filter(d, fields):
    """
    filter dict based on fields

    Args:
        d (dict): dictionary to be filtered
        fields (list): list of strings -- iterested fields
    """
    return {k: v for k, v in d.items() if k in fields}

def dict_filter_value0(d, fields):
    """
    filter dict based on fields and then extract the first element of list-typed values

    Args:
        d (dict): dictionary to be filtered
        fields (list): list of strings -- iterested fields
    """
    return {k: v[0] for k, v in d.items() if k in fields}

def report_map(root):
    """
    map single report into a flat dictionary
    """
    patient = root['patient']
    root_dict = dict_filter(root, ROOT_FIELDS)
    patient_dict = dict_filter(patient, PATIENT_FIELDS)
    reaction_list = [dict(chain.from_iterable(d.items() for d in (root_dict, patient_dict, dict_filter(r, REACTION_FIELDS)))) for r in patient['reaction']]
    drug_list = [dict_filter_value0(p['openfda'], DRUG_FIELDS) for p in patient['drug'] if 'openfda' in p]  # skip those without openfda entry
    # cross product of the two lists
    return [dict(chain.from_iterable(d.items() for d in (r, d))) for r in reaction_list for d in drug_list]

def get_reports_df(reports):
    """
    get a pandas DataFrame from list of reports
    """
    flat_dict = (report_map(r) for r in reports)
    return pd.DataFrame([item for l in flat_dict for item in l])
