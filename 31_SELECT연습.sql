SELECT * FROM wntrade.고객;
SELECT * FROM wntrade.주문세부;
SELECT*FROM 고객;
select 고객번호, 고객회사명 from 고객;
select 고객번호, 담당자명, 고객회사명 as 이름, 마일리지 as 포인트 from 고객;
select 사원번호, 이름 as 직원명, 주소, 직위 from 사원;
select * from 제품;
select 제품명 as 제품정보
		, FORMAT(단가, 0) AS 단가
        , 재고 as '구매 가능 수량'
        , FORMAT(단가*재고, 0) as '주문가능금액'
from 제품;

SELECT 주문번호 FROM 주문세부;
SELECT 제품번호
	, FORMAT(단가,0) AS 단가
    , 주문수량
    , 할인율
    , FORMAT(주문수량*단가*(1-할인율),0) AS 주문금액
FROM 주문세부
ORDER BY 주문수량*단가*할인율 DESC;

SELECT 고객번호
	,담당자명
    ,고객회사명
    , FORMAT(마일리지,0) AS 포인트
    , FORMAT(마일리지*1.1,0) AS '10%인상된 마일리지'
FROM 고객;

SELECT 고객번호
	,담당자명
    ,마일리지
FROM 고객
WHERE 마일리지 >= 100000;

SELECT 제품번호
	, 제품명
    , 재고
FROM 제품
WHERE 단가 >= 10000;

SELECT *FROM 제품
WHERE 단가 >= 10000;

select 제품명 as 제품정보
		, FORMAT(단가, 0) AS 단가
        , 재고 as '구매 가능 수량'
        , FORMAT(단가*재고, 0) as '주문가능금액'
from 제품
WHERE 단가*재고 > 10000
ORDER BY 재고 DESC;

SELECT * FROM 사원
WHERE 직위 = '사원';

SELECT 고객번호
	,담당자명
    ,도시
    ,마일리지 AS 포인트
FROM 고객
WHERE 도시 = '서울특별시'
ORDER BY 마일리지 DESC;

SELECT *
FROM 고객
LIMIT 3;

SELECT *
FROM 고객
ORDER BY 마일리지 DESC
LIMIT 3;

SELECT * FROM 고객
WHERE 마일리지 >= 1000
ORDER BY 담당자명
LIMIT 10;

SELECT * FROM 마일리지등급
ORDER BY 하한마일리지 DESC
LIMIT 3;

SELECT 직위
	, 이름
    , 입사일
FROM 사원
WHERE 도시 = '서울특별시'
ORDER BY 생일 DESC
LIMIT 10;

SELECT DISTINCT 도시
FROM 고객;

SELECT 23+5 AS 더하기
	,23-5 AS 빼기
    ,23*5 AS 곱하기
    ,23/5 AS 실수나누기
    ,23 DIV 5 AS 정수나누기
    ,23%5 AS 나머지1
    ,23 MOD 5 AS 나머지2;

SELECT 23 >=5
	,23 <= 5
    ,23 > 23
    ,23 < 23
    ,23 = 23
    ,23 != 23
    ,23 <> 23;
    
SELECT *
FROM 고객
WHERE 담당자직위 <> '대표 이사';

SELECT * FROM 주문
WHERE 주문일 <= '2021-01-01';

DESCRIBE 주문;

SELECT *
FROM 고객
WHERE 도시 = '부산광역시'
AND 마일리지 < 1000;

-- 서울, 마일리지 5000 이상
SELECT *
FROM 고객
WHERE 도시 = '서울특별시' AND 마일리지 >= 5000;

-- 서울이거나 마일리지 10000 이상
SELECT * FROM 고객
WHERE 도시 = '서울특별시' OR 마일리지 >= 10000;

-- 서울특별시가 아닌 고객
SELECT * FROM 고객
WHERE NOT 도시 = '서울특별시';

-- 서울이 아니면서 마일리지 5000이상
SELECT * FROM 고객
WHERE NOT 도시 = '서울특별시' AND 마일리지 >= 5000;

-- 서울특별시, 부산광역시 고객
SELECT * FROM 고객
WHERE 도시 = '서울특별시' OR 도시 = '부산광역시';

SELECT 고객번호
	,담당자명
    ,마일리지
    ,도시
FROM 고객
WHERE 도시 = '부산광역시'
UNION ALL
SELECT 고객번호
	,담당자명
    ,마일리지
    ,도시
FROM 고객
WHERE 마일리지 < 1000
ORDER BY 1;

-- 단가가 5000 이상이거나 할인율이 0이 아닌 고객
SELECT * FROM 주문세부
WHERE 단가 >= 5000 OR 할인율 > 0;

-- 고객 도시, 사원 도시 모두 출력
SELECT 도시
FROM 고객
UNION
SELECT 도시
FROM 사원;

SELECT *
FROM 고객
WHERE 지역 IS NULL;

SELECT * FROM 고객 ORDER BY 지역;

UPDATE 고객
SET 지역 = NULL
WHERE 지역 = '';

SELECT 고객번호
	,담당자명
    ,담당자직위
FROM 고객
WHERE 담당자직위 = '영업 과장'
OR 담당자직위 = '마케팅 과장';

SELECT 고객번호
	,담당자명
    ,담당자직위
FROM 고객
WHERE 담당자직위 IN('영업 과장', '마케팅 과장');

SELECT 담당자명
	,마일리지
FROM 고객
WHERE 마일리지 >= 100000
AND 마일리지 <= 200000;

SELECT 담당자명
	,마일리지
FROM 고객
WHERE 마일리지 BETWEEN 100000 AND 200000;

-- IN,BETWEEN AND
# 부서가 A1, A2인 사원
SELECT * FROM 사원
WHERE 부서번호 IN('A1','A2');

# 주문일이 2020-06-01 ~ 2020-06-11
SELECT * FROM 주문
WHERE 주문일 BETWEEN '2020-06-01' AND '2020-06-11';

SELECT * FROM 고객 WHERE 담당자명 BETWEEN '권기호' AND '김도현' ORDER BY 담당자명;

USE wntrade;

SELECT 고객번호
	, 담당자명
    , 고객회사명
    , 전화번호
    , CASE
        WHEN 전화번호 REGEXP '^02[0-9]{7}$' THEN
            CONCAT(
                '(02)-',
                SUBSTRING(전화번호, 3, 3),
                '-',
                SUBSTRING(전화번호, 6, 4)
            )
        WHEN 전화번호 REGEXP '^[0-9]{10}$' THEN
            CONCAT(
                '(',
                SUBSTRING(전화번호, 1, 3),
                ')-',
                SUBSTRING(전화번호, 4, 3),
                '-',
                SUBSTRING(전화번호, 7, 4)
            )
      END AS 전화번호_표시용
FROM 고객
WHERE 고객번호 LIKE '_C%';

SELECT * FROM 고객
WHERE 고객번호 LIKE 'C%';

SELECT * FROM 고객
WHERE 고객번호 LIKE '__C%';

SELECT * FROM 고객
WHERE 고객번호 LIKE '%C';

SELECT * FROM 고객
WHERE 도시 LIKE '%광역시'
		AND (고객번호 LIKE '_C___' OR 고객번호 LIKE '__C__'); #우선순위 ()

/* QUERY 질의문 - SELECT 행단위로 추출하는 명령
 * SELECT 컬럼목록 - 값의 목록 지정, AS, 수식 사용법
 * FROM 테이블목록
 * WHERE 조건식
 * ORDER BY 컬럼목록 - 출력을 정렬 - ASC, DESC
 * LIMIT N - 출력의 개수 지정
 * DISTINCT - 컬럼에 나오는 값의 목록
 * */

/* 쿼리 실행순서
 * FROM
 * WHERE
 * SELECT
 * ORDER BY
 * LIMIT
 * */
 
/* 연산자
 * 수치연산자, 비교연산자, 논리연산자, 집합연산자(UNION, UNION ALL)
 * IS NULL
 * IN, BETWEEN AND
 * */
 
/* SQL문 작성 규칙
 * 대소문자 구분 X - 명령어, 테이블명, 컬럼명(단, 컬럼값 제외)
 * 여러 줄에 걸쳐 작성 O -> 마지막에 ; 필수 "들여쓰기"
 * 명령어는 대문자로 쓰는 것이 일반적
 * 컬럼목록, 테이블 목록은 ,(콤마)로 연결한다. 순서 중요
 * */