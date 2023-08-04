import re
from sympy import sympify
import pandas as pd

def extractVariable(text):
    pattern = r'\(([a-zA-Z0-9_]+)\)'
    matches = re.findall(pattern, text)
    return matches

def strToFormula(formula_str):
    try:
        formula = sympify(formula_str)
        return formula
    except Exception as e:
        print("Error: ", e)
        return None
    
def assignRemark(date):
    if date < pd.to_datetime('2023-08-01'):
        return 'Before'
    else:
        return 'After'
    
def getVarValues(df, variables, remark):
    var_values_pair = []
    for variable in variables:
        var_value = df.loc[df['Remark']==remark][variable.lower()].values[0]
        var_values_pair.append(tuple((variable,var_value)))

    return var_values_pair

def createKpiComparison(df_kpi, df_formula, kpi_list, before_date='', after_date='', comp_duration='', excl_date_list=[]):
    output_list = []
    df_kpi.columns = df_kpi.columns.str.lower()

    for kpi in kpi_list:
        kpi_formula_str = df_formula.loc[df_formula['KPI']==kpi].Formula.values[0]
        print(kpi_formula_str)
        variables = extractVariable(kpi_formula_str)
        print(variables)

        df_kpi['date_id'] = pd.to_datetime(df_kpi['date_id'])
        df_kpi['Remark'] = df_kpi['date_id'].apply(assignRemark)

        df_summary = df_kpi.groupby('Remark',as_index=False).sum()

        ## filter date here ##

        ######################

        kpi_formula = strToFormula(kpi_formula_str)

        kpi_after = kpi_formula.subs(getVarValues(df_summary,variables,'After'))
        kpi_before = kpi_formula.subs(getVarValues(df_summary,variables,'Before'))

        output_list.append([kpi,
                            float(kpi_before),
                            float(kpi_after)])
    
    df_output = pd.DataFrame(output_list, columns=['KPI','Before','After'])

    return df_output