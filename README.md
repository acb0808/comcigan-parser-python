# comcigan-parser-python

본 라이브러리는 `Python` 환경에서 사용할 수 있는 컴시간 알리미 시간표 파싱 라이브러리 입니다.  

본 라이브러리는 광명경영회계고등학교에 다니고 있는 것으로 추정되는 [이근혁](https:#github.com/leegeunhyeok) 님의 `Node.js` 파싱 라이브러리를 `Python`언어로 변환 한 것입니다.

자세한 세부 라이선스나 정보를 알고싶으시다면 `Node.js` 라이브러리 [깃허브](https:#github.com/leegeunhyeok/comcigan-parser/)를 참고하여 주세요.

본 라이브러리는 [컴시간](http:#컴시간학생.kr) 홈페이지에서 등록된 학교의 **시간표** 데이터를 파싱하여 제공합니다.

## 기능

- 학교명 입력 후 바로 사용 가능
- 학급 시간표 데이터 제공

## 세부사항

> 자세한 [세부사항](https:#github.com/leegeunhyeok/comcigan-parser/)을 확인해주세요 아래는 [원작자](https:#github.com/leegeunhyeok)분이 만드신 라이브러리입니다.

- [광명경영회계고등학교 카카오 자동응답 API 챗봇](https:#github.com/leegeunhyeok/GMMAHS-KAKAO)
- [광명경영회계고등학교 카카오 오픈빌더 i 챗봇](https:#github.com/leegeunhyeok/GMMAHS-KAKAO-i)

## 사용전

컴시간 서비스를 사용하는 학교의 시간표 데이터를 쉽게 수집하여 사용할 수 있습니다.


> (주의!) 본 라이브러리는 비공식적으로 컴시간 서비스의 데이터를 파싱하며, 상업적인 용도로 사용하다 문제가 발생할 경우 본 라이브러리 개발자는 책임을 지지 않습니다.

```bash
pip install bs4
pip install requests
pip install js2py
```

혹은 [comcigan](https:#pypi.org/project/comcigan/#description) 패키지를 사용하셔도 똑같은 결과가 나옵니다
```bash
pip install comcigan
```

## 개발 문서

### Timetable

Timetable 클래스의 인스턴스를 생성하여 사용합니다.

모듈을 불러오면 Timetable 클래스의 인스턴스를 생성할 수 있습니다.

```py
import comcigan_parser
timetable = comcigan_parser.Timetable();
```

---

### Timetable.init()

인스턴스 정보를 초기화 합니다.  
옵션을 추가하여 사용자 설정을 진행할 수 있습니다.

```py
timetable.init(options);
```

| Parameter |  Type  | Required |
| :-------- | :----: | :------: |
| option    | object |    X     |

옵션 정보는 아래 표 참고

| Option   | Value  | default | Required |
| :------- | :----: | :-----: | :------: |
| maxGrade | number |    3    |    X     |
| cache    | number |    0    |    X     |

- `maxGrade`: 최대 학년을 지정합니다. (초등: 6, 중/고등: 3)
- `cache`: 시간표 데이터 캐싱 시간(ms)을 지정합니다 (기본값: 0 - 비활성)
  - 시간을 지정하면, 데이터 조회 시 지정한 시간만큼 임시로 보관하고 있다가, 이후 새로운 조회할 때 보관하던 결과 데이터를 즉시 반환합니다.
  - 지정한 캐싱 시간이 지나면 새로 수집하며, 다시 캐싱 시간만큼 보관합니다.

Return - `None`

---

### Timetable.search()

학교 정보를 검색합니다.

> 컴시간에 등록된 학교가 아닐 경우 검색되지 않습니다.

```py
timetable.search(keyword);
```

| Parameter |  Type  | Required |
| :-------- | :----: | :------: |
| keyword   | string |    O     |

Return - `list <학교데이터[]>`

학교 데이터는 [여기](#학교-데이터) 참고

---

### Timetable.setSchool()

시간표를 불러올 학교를 지정합니다. 학교 코드는 학교 검색을 통해 확인할 수 있습니다.

```py
timetable.setSchool(schoolCode);
```

| Parameter |  Type  | Required |
| :-------- | :----: | :------: |
| keyword   | number |    O     |

Return - `None`

---

### Timetable.getTimetable()

지정한 학교의 시간표 데이터를 불러옵니다.

```py
timetable.getTimetable();
```

Return - `dict<시간표>`

---

### Timetable.getClassTime()

각 교시별 수업 시작/종료 시간정보를 반환합니다.

```py
timetable.getClassTime();
```

Return - `list<string>`

---

## 사용 방법

### Timetable 인스턴스 생성

`comcigan-parser` 모듈을 불러온 후 인스턴스를 생성합니다.  
생성 시에  `option`인자를 사용하여 옵션을 지정할 수 있습니다.

- 옵션은 [여기](#timetableinit) 참조

```py
import comcigan_parser
timetable = comcigan_parser.Timetable();
```

---

### 학교 검색

컴시간에 등록되어있는 학교를 검색하여 결과를 반환합니다.

> 검색 결과가 없는 경우 예외가 발생합니다.

```py
timetable.search('하안')
  # schoolList
  # [{'_': 24966, 'region': '경기', 'name': '하안중학교', 'code': 65187}, {'_': 24966, 'region': '경기', 'name': '하안북중학교', 'code': 36051}]
```

---

### 학교 설정

컴시간에 등록되어있는 학교를 검색하고 인스턴스에 등록합니다.

> 학교가 여러개 조회되거나 검색 결과가 없는 경우 예외가 발생합니다.

```py
mySchool = timetable.findSchool({'region':'경기', 'name':'하안북중학교'}, schoolList)

timetable.setSchool(mySchool['code'])
```

---

### 시간표 조회

등록한 학교의 시간표 데이터를 조회합니다.

```py
  result = timetable.getTimetable()

  # result[학년][반][요일][교시]
  # 요일: (월: 0 ~ 금: 4)
  # 교시: 1교시(0), 2교시(1), 3교시(2)..
  # 3학년 10반 화요일 2교시 시간표
  console.log(result[3][10][1][1]);
```

---

### 수업시간 정보 조회

수업 시간 정보를 반환힙니다.

```py
timetable.getClassTime();
```

---

## 활용 예시

sample.

## 데이터 형식

### 학교 데이터

```py
{
  '_': 24966, # 알 수 없는 코드
  'region':'경기', # 지역
  'name': '하안북중학교', # 학교명
  'code': 13209 # 학교코드
}
```

### 시간표 데이터

```py
{
  "1": {
    # 1학년
    "1": [ # 1반
      [ # 월요일 시간표
        {
          'grade': 1,                   # 학년
          'class': 1,                   # 반
          'weekday': 1,                 # 요일 (1: 월 ~ 5: 금)
          'weekdayString': '월',         # 요일 문자열
          'classTime': 1,              # 교시
          'teacher': '이주',            # 선생님 성함
          'subject': '기술'     # 과목명
        },
        {
          'grade': 1,
          'class': 1,
          'weekday': 1,
          'weekdayString': '월',
          'classTime': 2,
          'teacher': '황경',
          'subject': '사회'
        }
      ],
      [화요일시간표],
      [수요일시간표],
      [목요일시간표],
      [금요일시간표]
    ],
    "2": [ # 2반
      [월요일시간표],
      [화요일시간표],
      [수요일시간표],
      [목요일시간표],
      [금요일시간표]
    ],
    "3": [
      [], [], [], [], []
    ],
    ...
  },
  "2": {
    # 2학년
  },
  "3": {
    # 3학년
  }
}
```

각 시간표 데이터 형식

- 각 요일 `Array` 에는 아래와 같은 형식의 데이터가 포함되어있음

```py
[
  {
    'grade': 1,                   # 학년
    'class': 1,                   # 반
    'weekday': 1,                 # 요일 (1: 월 ~ 5: 금)
    'weekdayString': '월',         # 요일 문자열
    'classTime': 1,              # 교시
    'teacher': '이주',            # 선생님 성함
    'subject': '기술'     # 과목명
  },
  {
    'grade': 1,
    'class': 1,
    'weekday': 1,
    'weekdayString': '월',
    'classTime': 2,
    'teacher': '황경',
    'subject': '사회'
  }
  ...
]
```

### 수업시간 정보

```py
['1(09:15)', '2(10:10)', '3(11:05)', '4(12:00)', '5(13:35)', '6(14:30)', '7(15:25)', '8(16:20)']
```

응용 방법

```py
result = timetable.getTimetable()

# 3학년 8반 시간표 (월 ~ 금)
print(result[3][8])

# 1학년 1반 월요일 시간표
print(result[1][1][0]);

# 2학년 5반 금요일 3교시 시간표
print(result[2][5][4][2]);
```

- 학년, 반의 경우 인덱스 상관 없이 동일하게 접근
  - 예: 1학년 3반(result[1][3]), 3학년 9반(result[3][9])
- 요일, 교시의 경우 인덱스는 0부터 시작하므로 -1 값을 통해 접근
  - 예: 월요일 3교시(result[..][..][0][2])

## 문제 신고

시간표 파싱이 되지 않거나 문제가 발생한 경우 [이슈](https:#github.com/leegeunhyeok/comcigan-parser/issues)를 남겨주세요.

