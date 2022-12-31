# ddareung

## 서울시 따릉이 적자문제 해결 프로젝트
## jupyter내용 확인: https://nbviewer.org/github/dhcryan/ddareung/blob/master/module/seoul_bike.ipynb



## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
```
.
|──────app/
| |────__init__.py
| |────api/
| | |────__init__.py
| | |────cve/
| | |────user/
| | |────oauth/
| |──────config.Development.cfg
| |──────config.Production.cfg
| |──────config.Testing.cfg
| |────dao/
| |────model/
| |────oauth/
| |────util/
|──────run.py
|──────tests/

```
