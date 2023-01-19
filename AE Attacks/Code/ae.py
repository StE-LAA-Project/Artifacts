import os,sys
from collections import Counter

def check_fields_det(aux_csv,ciph_csv,aux_field_no,ciph_field_no,is_int=False):
	# We do frequency analysis on deterministic encryption.

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[aux_field_no].replace('"','') for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[ciph_field_no].replace('"','') for line in lines]

	if is_int:
		aux_field_int = [int(x) for x in aux_field]
		ciph_field_int = [int(x) for x in ciph_field]
		aux_field = aux_field_int
		ciph_field = ciph_field_int
	else:
		aux_field_upper = [x.upper() for x in aux_field]
		ciph_field_upper = [x.upper() for x in ciph_field]
		aux_field = aux_field_upper
		ciph_field = ciph_field_upper

	aux_field_counter = Counter(aux_field)
	ciph_field_counter = Counter(ciph_field)

	res = []
	for p in [aux_field_counter,ciph_field_counter]:
		tmp_list = []
		for key in p:
			tmp_list.append((key,p[key]))
		tmp_list.sort(key=lambda x:x[1],reverse=True)
		res.append(tmp_list)

	aux_num = len(res[0])
	ciph_num = len(res[1])

	v_score_int = 0
	r_score_int = 0
	for i in range(min(aux_num,ciph_num)):
		if res[0][i][0] == res[1][i][0]:
			v_score_int += 1
			r_score_int += res[1][i][1]
	v_score = v_score_int/ciph_num
	r_score = r_score_int/len(ciph_field)
	print(v_score,r_score)

def check_fields_ran(aux_csv,ciph_csv,aux_field_no,ciph_field_no,is_int=False):
	# For random encryption, we assume no null values (they can't be encrypted).
	# As our databases are of the same size, we can just sort and compare the columns.
	# For rand enc, V-score doesn't really make sense (some classes can be partially correct).

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[aux_field_no].replace('"','') for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[ciph_field_no].replace('"','') for line in lines]

	if is_int:
		aux_field_int = [int(x) for x in aux_field]
		ciph_field_int = [int(x) for x in ciph_field]
		aux_field = [x//max(1,-1) for x in aux_field_int] # For max(1,-1): Returns -1 only when negative, else unchanged
		ciph_field = [x//max(1,-1) for x in ciph_field_int]

	assert(len(aux_field)==len(ciph_field))
	N = len(aux_field)
	aux_field.sort()
	ciph_field.sort()
	if not is_int:
		correct = sum([aux_field[i].upper()==ciph_field[i].upper() for i in range(N)])
		print(correct/N)
	else:
		correct = sum([aux_field[i]==ciph_field[i] for i in range(N)])
		print(correct/N)

def check_fields_det_gender(aux_csv,ciph_csv):

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[5] for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[12].replace('"','') for line in lines]

	convert_aux = {'M':0, 'F':1, 'U':-1, '':-2} # All the negatives will be wrong
	convert_ciph = {'0':0, '1':1, '-6':-6, '-8':-8, '-9':-9}
	aux_field_int = [convert_aux[x] for x in aux_field if convert_aux[x]>=0] # Throw away negative
	ciph_field_int = [convert_ciph[x] for x in ciph_field if convert_ciph[x]>=0]
	aux_field = aux_field_int
	ciph_field = ciph_field_int

	aux_field_counter = Counter(aux_field)
	ciph_field_counter = Counter(ciph_field)

	res = []
	for p in [aux_field_counter,ciph_field_counter]:
		tmp_list = []
		for key in p:
			tmp_list.append((key,p[key]))
		tmp_list.sort(key=lambda x:x[1],reverse=True)
		res.append(tmp_list)

	aux_num = len(res[0])
	ciph_num = len(res[1])

	v_score_int = 0
	r_score_int = 0
	for i in range(min(aux_num,ciph_num)):
		if res[0][i][0] == res[1][i][0]:
			v_score_int += 1
			r_score_int += res[1][i][1]
	v_score = v_score_int/ciph_num
	r_score = r_score_int/len(ciph_field)
	print(v_score,r_score)

def check_fields_det_race(aux_csv,ciph_csv):

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[6] for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[34].replace('"','') for line in lines]

	convert_aux = {'1':5, '2':4, '3':2, '4':3, '5':1, '6':6, '7':7, '9':9} # Essentially int(x)
	convert_ciph = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '-8':-8, '-9':-9}
	aux_field_int = [convert_aux[x] for x in aux_field if convert_aux[x]<=6] # TODO: throw away 7 and 9?
	ciph_field_int = [convert_ciph[x] for x in ciph_field if convert_ciph[x]>=0] # Throw away negative
	aux_field = aux_field_int
	ciph_field = ciph_field_int

	aux_field_counter = Counter(aux_field)
	ciph_field_counter = Counter(ciph_field)

	res = []
	for p in [aux_field_counter,ciph_field_counter]:
		tmp_list = []
		for key in p:
			tmp_list.append((key,p[key]))
		tmp_list.sort(key=lambda x:x[1],reverse=True)
		res.append(tmp_list)

	aux_num = len(res[0])
	ciph_num = len(res[1])

	v_score_int = 0
	r_score_int = 0
	for i in range(min(aux_num,ciph_num)):
		if res[0][i][0] == res[1][i][0]:
			v_score_int += 1
			r_score_int += res[1][i][1]
	v_score = v_score_int/ciph_num
	r_score = r_score_int/len(ciph_field)
	print(v_score,r_score)

def check_fields_ran_gender(aux_csv,ciph_csv):
	# Databases are of different sizes - do "lazy" scaling

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[5] for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[12].replace('"','') for line in lines]

	convert_aux = {'M':0, 'F':1, 'U':-1, '':-1}
	convert_ciph = {'0':0, '1':1, '-6':-1, '-8':-1, '-9':-1}
	aux_field_int = [convert_aux[x] for x in aux_field if convert_aux[x]>=0]
	ciph_field_int = [convert_ciph[x] for x in ciph_field if convert_ciph[x]>=0]
	aux_field = aux_field_int
	ciph_field = ciph_field_int

	N_aux = len(aux_field)
	N_ciph = len(ciph_field)
	aux_counters = [0]*2
	for i in range(2):
		aux_counters[i] = round(aux_field.count(i)/N_aux * N_ciph)
	offset = N_ciph - sum(aux_counters) # can be negative
	
	# Scale lazily - round errors to single class
	aux_counters[0] += offset # Assumes final result >= 0

	aux_field = []
	for i in range(2):
		aux_field += [i]*aux_counters[i]
	
	assert(len(aux_field)==N_ciph)
	aux_field.sort()
	ciph_field.sort()
	correct = sum([aux_field[i]==ciph_field[i] for i in range(N_ciph)])
	print(correct/N_ciph)

def check_fields_ran_race(aux_csv,ciph_csv):
	# Databases are of different sizes - do "lazy" scaling

	with open(aux_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	aux_field = [line.rstrip('\n').split(',')[6] for line in lines]
	with open(ciph_csv,'r') as f:
		lines = f.readlines()
	lines = lines[1:]
	ciph_field = [line.rstrip('\n').split(',')[34].replace('"','') for line in lines]

	convert_aux = {'1':5, '2':4, '3':2, '4':3, '5':1, '6':6, '7':7, '9':-1}
	convert_ciph = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '-8':-1, '-9':-1}
	aux_field_int = [convert_aux[x] for x in aux_field if convert_aux[x]<=6]
	ciph_field_int = [convert_ciph[x] for x in ciph_field if convert_ciph[x]>=0]
	aux_field = aux_field_int
	ciph_field = ciph_field_int
	N_aux = len(aux_field)
	N_ciph = len(ciph_field)
	aux_counters = [0]*7
	for i in range(7):
		aux_counters[i] = round(aux_field.count(i)/N_aux * N_ciph)
	offset = N_ciph - sum(aux_counters) # can be negative
	
	# Scale lazily - round errors to single class
	aux_counters[1] += offset # Assumes final result >= 0

	aux_field = []
	for i in range(7):
		aux_field += [i]*aux_counters[i]
	
	assert(len(aux_field)==N_ciph)
	aux_field.sort()
	ciph_field.sort()
	correct = sum([aux_field[i]==ciph_field[i] for i in range(N_ciph)])
	print(correct/N_ciph)

if __name__ == "__main__":
	florida_csv = sys.argv[1]
	ohio_csv = sys.argv[2]
	nis2018_csv = sys.argv[3]
	nis2019_csv = sys.argv[4]
	SQL_fields_2018 = ['Age_in_years_at_admission','Neonatal_age_first_28_days_after_birth_indicator','Admission_month','Admission_day_is_a_weekend','Died_during_hospitalization','NIS_discharge_weight','Disposition_of_patient_uniform','Discharge_quarter','DRG_in_effect_on_discharge_date','DRG_grouper_version_used_on_discharge_date','DRG_in_use_on_discharge_date_calculated_without_POA','Elective_versus_non_elective_admission','Indicator_of_sex','HCUP_Emergency_Department_service_indicator','Census_Division_of_hospital','NIS_hospital_number','ICD_10_CM_Diagnosis_1','ICD_10_CM_Number_of_diagnoses_on_this_record','ICD_10_PCS_Number_of_procedures_on_this_record','ICD_10_PCS_Procedure_1','NIS_record_number','Length_of_stay_cleaned','MDC_in_effect_on_discharge_date','MDC_in_use_on_discharge_date_calculated_without_POA','NIS_hospital_stratum','Primary_expected_payer_uniform','Patient_Location_NCHS_Urban_Rural_Code','Number_of_days_from_admission_to_I10_PR1','Race_uniform','Total_charges_cleaned','Transfer_in_indicator','Transfer_out_indicator','Calendar_year','Median_household_income_national_quartile_for_patient_ZIP_Code']
	SQL_fields_2019 = ['Age_in_years_at_admission','Neonatal_age_first_28_days_after_birth_indicator','Admission_month','Admission_day_is_a_weekend','Died_during_hospitalization','NIS_discharge_weight','Disposition_of_patient_uniform','Discharge_quarter','DRG_in_effect_on_discharge_date','DRG_grouper_version_used_on_discharge_date','DRG_in_use_on_discharge_date_calculated_without_POA','Elective_versus_non_elective_admission','Indicator_of_sex','HCUP_Emergency_Department_service_indicator','Census_Division_of_hospital','NIS_hospital_number','ICD_10_CM_Birth_Indicator','ICD_10_CM_Delivery_Indicator','ICD_10_CM_Diagnosis_1','Injury_ICD_10_CM_diagnosis_reported_on_record_1_First_listed_injury_2_Other_than_first_listed_injury_0_No_injury','Multiple_ICD_10_CM_injuries_reported_on_record','ICD_10_CM_Number_of_diagnoses_on_this_record','ICD_10_PCS_Number_of_procedures_on_this_record','ICD_10_PCS_Procedure_1','ICD_10_CM_PCS_Hospital_Service_Line','NIS_record_number','Length_of_stay_cleaned','MDC_in_effect_on_discharge_date','MDC_in_use_on_discharge_date_calculated_without_POA','NIS_hospital_stratum','Primary_expected_payer_uniform','Indicates_operating_room_major_diagnostic_or_therapeutic_procedure_on_the_record','Patient_Location_NCHS_Urban_Rural_Code','Number_of_days_from_admission_to_I10_PR1','Race_uniform','Total_charges_cleaned','Transfer_in_indicator','Transfer_out_indicator','Calendar_year','Median_household_income_national_quartile_for_patient_ZIP_Code']
	SQL_fields_selected = ['Age_in_years_at_admission','Neonatal_age_first_28_days_after_birth_indicator','Admission_month','Admission_day_is_a_weekend','Died_during_hospitalization','DRG_in_effect_on_discharge_date','MDC_in_effect_on_discharge_date','ICD_10_CM_Diagnosis_1','Number_of_days_from_admission_to_I10_PR1','Indicator_of_sex','Race_uniform']

	## Deterministic ##
	print("Deterministic")
	for field_no in range(2):
		check_fields_det(florida_csv,ohio_csv,field_no,field_no)
	check_fields_det_gender(florida_csv,nis2019_csv)
	check_fields_det_race(florida_csv,nis2019_csv)
	for field in SQL_fields_selected:
		field_no_2018 = SQL_fields_2018.index(field)
		field_no_2019 = SQL_fields_2019.index(field)
		if field == 'ICD_10_CM_Diagnosis_1':
			check_fields_det(nis2018_csv,nis2019_csv,field_no_2018,field_no_2019)
		else:
			check_fields_det(nis2018_csv,nis2019_csv,field_no_2018,field_no_2019,is_int=True)

	## Random ##
	print("Random")
	for field_no in range(2):
		check_fields_ran(florida_csv,ohio_csv,field_no,field_no)
	check_fields_ran_gender(florida_csv,nis2019_csv)
	check_fields_ran_race(florida_csv,nis2019_csv)
	for field in SQL_fields_selected:
		field_no_2018 = SQL_fields_2018.index(field)
		field_no_2019 = SQL_fields_2019.index(field)
		if field == 'ICD_10_CM_Diagnosis_1':
			check_fields_ran(nis2018_csv,nis2019_csv,field_no_2018,field_no_2019)
		else:
			check_fields_ran(nis2018_csv,nis2019_csv,field_no_2018,field_no_2019,is_int=True)
