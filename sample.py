import comcigan_parser

timetable = comcigan_parser.Timetable();

schoolList = timetable.search('하안')
print(schoolList)
targetSchool = timetable.findSchool({'region':'경기', 'name':'하안북중학교'}, schoolList)

print(targetSchool)
timetable.setSchool(targetSchool['code'])

classTime = timetable.getClassTime()
print(classTime)
exit()
result = timetable.getTimetable()

for i in range(2):
    # 3학년 10반 목요일의 과목명
    # result[학년][반][요일][교시]
    #   -> grade, class, weekday, weekdayString, classTime, teacher, subject 반환
    print(result[1][1][0][i])



