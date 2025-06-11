import pandas as pd
import os
import win32com.client
import glob


# print('converting corrupted xls files to xlsx format')
# o = win32com.client.Dispatch("Excel.Application")
# o.Visible = False
# input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTank"
# output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\FacilityLocTankXLSX"
# files = glob.glob(input_dir + "/*.xls")

# for filename in files:
#     file = os.path.basename(filename)
#     output = output_dir + '/' + file.replace('.xls','.xlsx')
#     wb = o.Workbooks.Open(filename)
#     wb.ActiveSheet.SaveAs(output,51)
#     wb.Close(True)

# print('merging all the files into single file')
# CombinedCountyFile = pd.DataFrame()
# for Countyfile in os.listdir(output_dir):
#     fileDf= pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\FacilityLocTankXLSX\\"+str(Countyfile))
#     fileDf.columns = fileDf.iloc[12]
#     fileDf = fileDf[13:]
#     CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
# CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\FacLocTank.xlsx', index=False)

# print('converting corrupted xls files to xlsx format')
# o = win32com.client.Dispatch("Excel.Application")
# o.Visible = False
# input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstruction"
# output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankConstructionXLSX"
# files = glob.glob(input_dir + "/*.xls")

# for filename in files:
#     file = os.path.basename(filename)
#     output = output_dir + '/' + file.replace('.xls','.xlsx')
#     wb = o.Workbooks.Open(filename)
#     wb.ActiveSheet.SaveAs(output,51)
#     wb.Close(True)

# print('merging all the files into single file')
# CombinedCountyFile = pd.DataFrame()
# for Countyfile in os.listdir(output_dir):
#     fileDf= pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\TankConstructionXLSX\\"+str(Countyfile))
#     fileDf.columns = fileDf.iloc[12]
#     fileDf = fileDf[13:]
#     CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
# CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\TankConstruction.xlsx', index=False)

print('converting corrupted xls files to xlsx format')
o = win32com.client.Dispatch("Excel.Application")
o.Visible = False
input_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPiping"
output_dir = r"C:\Users\Administrator\Desktop\axon_states\states\Florida\TankPipingXLSX"
files = glob.glob(input_dir + "/*.xls")

for filename in files:
    file = os.path.basename(filename)
    output = output_dir + '/' + file.replace('.xls','.xlsx')
    wb = o.Workbooks.Open(filename)
    wb.ActiveSheet.SaveAs(output,51)
    wb.Close(True)

print('merging all the files into single file')
CombinedCountyFile = pd.DataFrame()
for Countyfile in os.listdir(output_dir):
    fileDf= pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\TankPipingXLSX\\"+str(Countyfile))
    fileDf.columns = fileDf.iloc[12]
    fileDf = fileDf[13:]
    CombinedCountyFile = CombinedCountyFile.append(fileDf,ignore_index= False)
CombinedCountyFile.to_excel(r'C:\Users\Administrator\Desktop\axon_states\states\Florida\Output\TankPiping.xlsx', index=False)


print('Processing All the dowloaded files and merging process started')
dfFLmap = pd.read_excel("C:\\Users\\Administrator\\Desktop\\axon_states\\states\\Florida\\Required\\FloridaMapping.xlsx")
print('Reading the Florida Mapping file....')
dfFLmap = dfFLmap[:0]

print('Reading FacLocTank file....')
AllTanks = pd.read_excel("C:\\Users\\Administrator\Desktop\\\axon_states\\states\\Florida\\Output\\FacLocTank.xlsx")

dfAllTanks = AllTanks[['FAC ID','TKID','FAC ADDR','FAC CITY','FAC ZIP','INSTALL','CAPACITY','CONTDESC','FAC NAME','COUNTY','TKSTAT']]
dfAllTanks.columns = ['Facility Id','Tank ID','Tank Location','City','Zipcode','Year Installed','Tank Size','content description','Facility Name','county','tank status']

