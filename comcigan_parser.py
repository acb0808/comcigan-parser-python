import requests, re, json, datetime, js2py, base64
from bs4 import BeautifulSoup
HOST = 'http://컴시간학생.kr';
HEADER = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'}

class Timetable:
    def __init__(self, option=None):
        '''
        * 시간표 파서를 초기화합니다.
        *
        * @param option 초기화 옵션 객체
        '''
        self._baseUrl = None;
        self._url = None;
        self._initialized = False;
        self._pageSource = None;
        self._cache = None;
        self._cacheAt = None;
        self._schoolCode = -1;
        self._weekdayString = ['일', '월', '화', '수', '목', '금', '토'];
        self._option = {
            'maxGrade': 3,
            'cache': 0,
        };
        if option != None:
            self._option = option
        req = requests.get(HOST, headers=HEADER)
        if str(req.status_code)[0] == '2':
            body = req.text
            frame = body.lower()
            frame = frame.replace("'", '"')
            frame = re.search(r'<frame[^>]*src=[\'"]?([^\'" >]+)', frame);
            if frame == None:
                raise SystemError('frame을 찾을 수 없습니다')
            

            uri = frame.group(1)
            frameHref = uri
            uri = re.search('http://(.*?)/', uri)
            if (uri == None):
                raise SystemError('접근 주소를 찾을 수 없습니다')
            uri = 'http://'+uri.group(1)

            self._url = frameHref;
            self._baseUrl = uri;
        else:
            raise SystemError("코드가 2번대가 아닙니다")

        req = requests.get(url=self._url, headers=HEADER)
        if str(req.status_code)[0] == '2':
            req.encoding = 'euc-kr'
            body = req.text
            
            idx = body.find('school_ra(sc)');
            idx2 = body.find("sc_data('");

            if (idx == -1 or idx2 == -1):
                raise SystemError('소스에서 식별 코드를 찾을 수 없습니다.')
            

            extractSchoolRa = body[idx:idx+50].replace(' ', '');
            schoolRa = re.search("url:'.(.*?)'", extractSchoolRa);
            # sc_data 인자값 추출
            extractScData = body[idx2:idx2+30].replace(' ', '');
            scData = re.search('\(.*?\)', extractScData);
            if scData != None:
                self._scData = re.sub('[()]', '', scData[0])
                self._scData = re.sub("'", '', self._scData)
                self._scData = self._scData.split(',');
            else:
                raise SystemError('sc_data 값을 찾을 수 없습니다.')
            

            if schoolRa != None:
                self._extractCode = schoolRa[1];
            else:
                raise SystemError('school_ra 값을 찾을 수 없습니다.')
            

            self._pageSource = body;
        else:
            raise SystemError("코드가 2번대가 아닙니다")
        self._initialized = True;
    def search(self, keyword):
        '''
        * 시간표 데이터를 불러올 학교를 설정합니다.
        *
        * @param {string} keyword 학교 검색 키워드
        * @returns 검색된 학교 목록 `Array<[코드, 지역, 학교이름, 학교코드]>`
        '''
        if (not self._initialized):
            raise SystemError('초기화가 진행되지 않았습니다.')
        

        hexString = '';
        for buf in str(keyword).encode('euc-kr'):
            hexString += '%' + hex(int(str(buf)))[2:]
        req = requests.get(self._baseUrl + self._extractCode + hexString, headers=HEADER)
        req.encoding = 'utf-8'
        body = str(req.text)
        jsonString = body[0: body.rfind('}') + 1];
        searchData = json.loads(jsonString)['학교검색'];

        if (str(req.status_code)[0] != '2'):
            raise SystemError("코드가 2번대가 아닙니다")

        if len(searchData) <= 0:
            raise SystemError('검색된 학교가 없습니다.')


        return list(map(lambda x:{"_":x[0], "region":x[1], "name":x[2], "code":x[3]}, searchData))
    
    def findSchool(self, val, List):
        for i in List:
            for j in val.keys():
                if i[j] != val[j]:
                    break
                if (list(val.keys()).index(j) == len(list(val.keys()))-1):
                    return i

    def setSchool(self, schoolCode):
        '''
        * 시간표를 조회할 학교 코드를 등록합니다
        *
        * @param school
        '''
        self._schoolCode = schoolCode;
        self._cache = None;
    
    def getTimetable(self):
        """
        * 설정한 학교의 전교 시간표 데이터를 불러옵니다
        *
        * @return 시간표 데이터
        """
        self._isReady();

        #캐시 지속시간이 존재하고, 아직 만료되지 않았다면 기존 값 전달
        #만료되었거나, 캐시가 비활성화(기본값)되어있는 경우엔 항상 새로운 값 파싱하여 전달
        if self._option['cache'] and not self._isCacheExpired():
            return self._cache;

        jsonString = self._getData();
        resultJson = json.loads(jsonString);
        startTag = re.search('<script language(.*?)>', self._pageSource)[0];
        regex = startTag + '(.*?)</script>'

        match = None
        script = '';
        #컴시간 웹 페이지 JS 코드 추출
        for match in [re.search(regex, self._pageSource)]:
            script += match[1];

        #데이터 처리 함수명 추출
        functioName = script
        functioName = re.search('function 자료[^\(]*', functioName)[0]
        functioName = re.sub('\+s', '', functioName)
        functioName = functioName.replace('function', '');
        #학년 별 전체 학급 수
        classCount = resultJson['학급수'];

        #시간표 데이터 객체
        timetableData = {};

        #1학년 ~ maxGrade 학년 교실 반복
        for grade in range(1, self._option['maxGrade']+1):
            try:
                timetableData[grade]
            except KeyError:
                timetableData[grade] = {};
                
            

            #학년 별 반 수 만큼 반복
            for classNum in range(1, classCount[grade]+1):
                try:
                    timetableData[grade][classNum]
                except KeyError:
                    timetableData[grade][classNum] = {};
                timetableData[grade][classNum] = self._getClassTimetable(
                    { 'data': jsonString, 'script': script, 'functioName':functioName },
                    grade,
                    classNum
                );

        self._cache = timetableData;
        self._cacheAt = datetime.datetime.now()
        return timetableData;

    def getClassTime(self):
        '''
        * 교시별 수업시간 정보를 조회합니다.
        * @returns
        '''
        self._isReady();
        # 교시별 시작/종료 시간 데이터
        return json.loads(self._getData())['일과시간'];
  

    def _getData(self) :
        '''
        * 컴시간의 API를 통해 전체 시간표 데이터를 수집/파싱하여 반환합니다.
        '''
        da1 = '0';
        s7 = self._scData[0] + str(self._schoolCode);
        s_acsii = str(s7 + '_' + da1 + '_' + self._scData[2]).encode('ascii')
        s_acsii_base64 = base64.b64encode(s_acsii)
        sc3 = self._extractCode.split('?')[0] + '?' +\
        s_acsii_base64.decode('ascii')
        # JSON 데이터 로드
        jsonString = None

        req = requests.get(self._baseUrl + sc3, headers=HEADER)
        req.encoding = 'utf-8'
        body = req.text
        if str(req.status_code)[0] != '2':
            raise SystemError('상태가 2번대가 아닙니다.')
        
        jsonString = body[0: body.rfind('}') + 1]

        return jsonString;

    def _getClassTimetable(self, codeConfig, grade, classNumber):
        '''
        * 지정된 학년/반의 1주일 시간표를 파싱합니다
        *
        * @param codeConfig 데이터, 함수명, 소스코드 객체
        * @param grade 학년
        * @param classNumber 반
        * @returns
        '''
        args = [codeConfig['data'], grade, classNumber];
        args = list(map(str, args))
        call = codeConfig['functioName'] + '(' + (','.join(args)) + ')';
        script = codeConfig['script'] + '\n\n' + call;



        # DEAD: Sorry about using eval() 
        res = js2py.eval_js(script);
        timetable = {}

        # Table HTML script
        soup = BeautifulSoup(res, 'html.parser')
        tr_list = soup.select('tr')
        # 1, 2번째 tr은 제목 영역이므로 스킵
        for timeIdx in range(len(tr_list)):
            currentTime = timeIdx - 2
            
            if timeIdx <= 1:
                continue

            td_list = tr_list[timeIdx].select('td')
            for weekDayIdx in range(len(td_list)):
                currentWeekDay = weekDayIdx - 1;
                
                # 처음(제목)과 끝(토요일) 영역은 스킵
                if (weekDayIdx == 0 or weekDayIdx == 6):
                    continue
                try:
                    timetable[currentWeekDay]
                except KeyError:
                    timetable[currentWeekDay] = {}

                contents = td_list[weekDayIdx].contents
                contents = "".join([str(x) for x in contents]).split('<br/>')
                subject = contents[0]
                teacher = contents[-1]

                timetable[currentWeekDay][currentTime] = {
                    'grade':grade,
                    'class': classNumber,
                    'weekday': weekDayIdx - 1,
                    'weekdayString': self._weekdayString[weekDayIdx],
                    'classTime': currentTime + 1,
                    'teacher':teacher,
                    'subject':subject,
                }
        return timetable
    
    def _isReady(self):
        '''
        * 초기화 및 학교 설정이 모두 준비되었는지 확인합니다.
        '''
        if not self._initialized:
            raise SystemError('초기화가 진행되지 않았습니다.');

        if self._schoolCode == -1:
            raise SystemError('학교 설정이 진행되지 않았습니다.');

    def _isCacheExpired(self):
        '''
        * 사용자가 세팅한 캐시 지속 시간을 확인하여 만료 여부를 반환합니다.
        *
        * @returns 캐시 만료 여부
        '''
        return datetime.datetime.now() - self._cacheAt >= self._option.cache;