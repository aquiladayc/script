import csv
import math
from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import tkinter as tk



source_csv = "C:\\python_workspace\\time_report\\Half of month.csv"
comment_txt = "C:\\python_workspace\\time_report\\comment.txt"

#Properties
userid = "USER"
password = "PASSWORD"
#Already created a time report for this period? If True, processing step is changed. 
isPending = False
#Comment for each time record
default_comm = "COMMENT"

#Fixed value
#login page
loginPageUrl = "http://psoftfin:8082/psp/fdmprd/TIMEREPORT/ERP/h/?cmd=logout&tab=DEFAULT"
#Create new report or open the pending report
createNewReportUrl = "http://psoftfin:8082/psp/fdmprd/TIMEREPORT/ERP/c/ADMINISTER_EXPENSE_FUNCTIONS.TE_TIME_ENTRY_INQ.GBL?TIME_SHEET_ID=0000325727" if isPending else "http://psoftfin:8082/psp/fdmprd/TIMEREPORT/ERP/s/WEBLIB_TE_NAV.WEBLIB_FUNCTION.FieldFormula.iScript_AddTimeReport?TE.Menu.Var=ADMIN&amp;PORTALPARAM_PTCNAV=EPTE_ADDTIMEREPORT&amp;EOPP.SCNode=ERP&amp;EOPP.SCPortal=TIMEREPORT&amp;EOPP.SCName=ADMN_TIME&amp;EOPP.SCLabel=&amp;EOPP.SCPTcname=PT_PTPP_SCFNAV_BASEPAGE_SCR&amp;FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.ADMN_TIME.ADMN_S200707051909519220557267&amp;IsFolder=false"
#Driver path
selenium_driver = "C:/python_workspace/time_report/webdriver/chromedriver.exe"
#holiday class, For workingday, class is "PSEDITBOX"
holiday_class = "MXGRAY"

#####################################################
#Read CSV source file
#####################################################


def extract_worktime():
    #Remove BOM from input file (For cosmetic)
    s = open(source_csv, mode='r', encoding='utf-8').read()
    open(source_csv, mode='w', encoding='utf-8').write(s)

    #read CSV 
    ###Expected format(column1 -> Project code, column2 -> work time)
    work_records = csv.reader(open(source_csv,  "r", encoding="utf-8"), delimiter=",", lineterminator="\r\n", quotechar='"', skipinitialspace=True)

    #Dictionary to store total working time for each project
    time_rec_dct = {}

    #Compute total working time for each project
    for work_rec in work_records:
        # print(work_rec)
        work_time_min = calc_time(work_rec[1])
        
        if work_time_min == 0:
            continue

        #If same key is already stored, total time should be combined
        if work_rec[0] in time_rec_dct:
            work_time_min = work_time_min + time_rec_dct[work_rec[0]]

        #store in dictionary
        time_rec_dct[work_rec[0]] = work_time_min

    #to minimize the diff caused by rounding, conversion is done at the end
    convert_min_to_hr(time_rec_dct)
    # print(time_rec_dct)
    return time_rec_dct

def convert_min_to_hr(time_rec_dct):

    for time_rec_key in time_rec_dct:
        #devided by 60, result is rounded up
        time_rec_dct[time_rec_key] = math.ceil(time_rec_dct[time_rec_key] / 60)
        # print(str(time_rec_key) + ':' + str(time_rec_dct[time_rec_key]))

#input string (hh:mm:ss)
#return in minute
def calc_time(work_time_str):
    #input is hh:mm:ss (ex. 3:23:09)
    work_time_list = work_time_str.split(":")
    # print(work_time_list)
    if work_time_list[0].isdecimal():
        hour_min = int(work_time_list[0]) * 60
        minute = int(work_time_list[1])
        #ignore seconds
        return  hour_min + minute
    else:
        return 0

####################################################
#Load Case IDs as comment
####################################################
def load_comments():
    #read file
    pFile = open(comment_txt,  "r", encoding="utf-8")
    lines = pFile.readlines()
    pFile.close()

    #pick up PJ code and Case ID
    comm_dict = {}
    case_ids = []
    for l in lines:
        fields = l.split('] [')
        case_id = fields[1].replace('[', '').replace(']','')
        #this case id is already loaded
        if case_id in case_ids:
            continue

        case_ids.append(case_id)
        pj = fields[0].replace('[', '').replace(']','')
        if pj in comm_dict:
            case_id = comm_dict[pj] + ', ' + case_id

        comm_dict[pj] = case_id
    
    print("----------Project:Case-------------")
    for comm in comm_dict:
        print(comm + ':' + comm_dict[comm])

    return comm_dict

#####################################################
#Open Report page
#####################################################

#Open the report page and return it
def getReportPage():
    driver = initWebDriver()
    login(driver)
    movetoReportPage(driver)

    return driver

# #returns webdriver for Chrome
def initWebDriver():
    #init WebDriver
    driver = webdriver.Chrome(selenium_driver)
    return driver

def login(driver):
    print("----------------Login--------------------")
    driver.get(loginPageUrl)
    driver.maximize_window()

    #set UserID/Password and submit
    driver.find_element_by_id("userid").send_keys(userid)
    driver.find_element_by_id("pwd").send_keys(password)
    driver.find_element_by_name("Submit").click()

def movetoReportPage(driver):
    print("----------------Going to report page--------------------")    

    #First page after the login
    driver.get(createNewReportUrl)

    if not isPending:
        iframe = driver.find_element_by_id("ptifrmcontent").find_element_by_id("ptifrmtarget").find_element_by_id("ptifrmtgtframe")
        #Add button is included in iframe. To be able to handle it, it should be once changed into normal frame
        driver.switch_to.frame(iframe)
        elem_add = driver.find_element_by_id("win0divSEARCHBELOW").find_element_by_id("#ICSearch")
        elem_add.click()

    sleep(5)

#####################################################
#Validation Util functions
#####################################################
def isHoliday(driver, date):
    #always take the first row
    target_id = "TIME" + str(date) + "$0"
    return True if driver.find_element_by_id(target_id).get_attribute("class") == holiday_class else False

    #Last date is over
def isFinished(driver, date):
    target_id = "TIME" + str(date) + "$0"
    try:
        driver.find_element_by_id(target_id).get_attribute("class")
        return False
    except NoSuchElementException:
        return True
   
def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#####################################################
#Inserting
#####################################################

def getTotalTime(driver, date):
    target_id = "TOT_TIME" + str(date) + "$0"
    t = driver.find_element_by_id(target_id).text
    if not is_number(t):
        #in case total time is not inserted
        return 0
    return int(float(t))

def getAlreadyInsertedTime(driver, date, row):
    #Prerequisite: vacation is already inserted and displayed as TotalTime
    inserted_time = getTotalTime(driver, date)

    #get inserted time for this date of all rows
    for i_row in range(row):
        target_id = "TIME" + str(date) + "$" + str(i_row)
        t = driver.find_element_by_id(target_id).get_attribute("value")
        if len(t) != 0:
            #in case the time is not inserted in this field
            inserted_time += int(float(t))

    return inserted_time

def displayTime(work_times):
    #formatting text
    dis_val = ""
    for k in work_times.keys():
        dis_val = dis_val + k + " : " + str(work_times[k]) + "\n"

    #show a popup
    popup = tk.Tk()
    popup.title("These are left to be inputed...")
    label = tk.Label(popup, text=dis_val)
    label.grid()
    popup.mainloop()

#work_time:Dict{PJ Code:Working time in hour}
def execInserting(driver, work_times):
    #load Comments at first
    comm_dict = load_comments()
    print("----------------Inserting your working records--------------------")

    if isPending:
        iframe = driver.find_element_by_id("ptifrmcontent").find_element_by_id("ptifrmtarget").find_element_by_id("ptifrmtgtframe")
        driver.switch_to.frame(iframe)    

    target_date = 1 #date count starts from 1
    target_row = 0 #row count starts from 0

    #Loop for projects  
    for wt_key in work_times.keys():
        #key format: PROJCTCODE_ACTIVITY_BILLINGTYPE
        project_info = wt_key.split("_")
        #print("project info:" + wt_key)
        pj_code = project_info[0]

        activity = project_info[1]
        bill_type = project_info[2]

        #html tags
        pj_id = "PROJECT$" + str(target_row)
        act_id = "ACTIVITY$" + str(target_row)
        bill_id = "EX_TIME_DTL_BILLING_ACTION$" + str(target_row)
        comm_id = "TE_COMMEN_WK_MX_COMMENTS_MX$" + str(target_row)

        sleep(5)
        #add a new row (First row is set by default)
        if not target_row == 0:
            driver.find_element_by_id("EX_TIME_DTL$new$" +str(target_row - 1) +"$$0").click()
            sleep(5)

        #Insert pj code, activity, billing type        
        driver.find_element_by_id(pj_id).clear()
        driver.find_element_by_id(pj_id).send_keys(pj_code)
        driver.find_element_by_id(act_id).clear()
        driver.find_element_by_id(act_id).send_keys(activity)
        driver.find_element_by_id(bill_id).send_keys(bill_type)
        sleep(5)

        #insert time
        while work_times[wt_key] > 0:
            #if all dates are filled but working time remains(working time is too long), exit process and show remaining time.
            if isFinished(driver, target_date):
                displayTime(work_times)

            if isHoliday(driver, target_date):
                target_date += 1
                continue

            remainTime = 8 # 1 day = 8 hours

            remainTime -= getAlreadyInsertedTime(driver, target_date, target_row)

            if remainTime <= 0:
                #this date is already filled
                target_date += 1
                continue

            #Text box for inserting time
            elem_time = driver.find_element_by_id("TIME" + str(target_date) + "$" + str(target_row))

            if remainTime > work_times[wt_key]:
                #ex) 6 hours are filled for this date, but working time is 4 hours
                #ex) Result 2 hours to fill, 0 working time -> Proceed to next project
                elem_time.send_keys(work_times[wt_key])
                remainTime -= work_times[wt_key]
                work_times[wt_key] = 0
            else:
                #ex) 2 hours are filled for this date, but working time is 4 hours
                #ex) Result 0 hours to fill, 2 working time -> Proceed to next date
                elem_time.send_keys(remainTime)
                work_times[wt_key] -= remainTime
                remainTime = 0
                #Goto the next date
                target_date += 1

        #insert comment
        if pj_code in comm_dict:
            comment = comm_dict[pj_code]
        else:
            comment = default_comm
    
        driver.find_element_by_id(comm_id).send_keys(comment)        
        target_row += 1

    print("############### Successfully Finish ! Ignore the error afterward ###############")
    #occur an error to keep the window open, otherwise it will be closed at the end of the process
    #please find a more beautiful way
    elem_act = driver.find_element_by_id("userid")

def main():
    #1 Open the report page
    #2 Extract Working time
    #3 Insert time
    driver = getReportPage()
    work_times = extract_worktime()
    execInserting(driver, work_times)

#Entry point
if __name__ == '__main__':
    main()