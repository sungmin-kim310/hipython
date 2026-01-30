USE WNTRADE;

SELECT FIELD('JAVA', 'SQL', 'JAVA', 'C')
		,FIND_IN_SET('JAVA', 'SQL,JAVA,C')
        ,INSTR('네 인생을 살아라', '인생')
        ,LOCATE('인생', '네 인생을 살아라');
        
SELECT FIELD('오땅','홈런볼','오땅','초콜릿');

SELECT REPLACE('010.1234.5678', '.', '-');

SELECT REVERSE('OLLEH');

SELECT NOW()
		,SYSDATE()
        ,CURDATE()
		,CURTIME();
        
SELECT NOW() AS 'START',SLEEP(5), NOW() AS 'END'; -- 쿼리 시작시간 기준
SELECT SYSDATE() AS 'START', SLEEP(5), SYSDATE() AS 'END'; -- 각 명령문 호출시간 기준

SELECT 고객번호,
IF(마일리지 >=1000, 'VIP', 'GOLD') AS 등급
FROM 고객;

SELECT 고객번호,
IF(도시 LIKE '서울%' OR 도시 LIKE '인천%' OR 도시 LIKE '경기%', '수도권', '비수도권') AS 수도권여부
FROM 고객;

SELECT 주문번호
		,FORMAT(단가,0) AS 단가
        ,주문수량
        ,FORMAT(단가*주문수량,0) AS 주문금액
		,CASE
			WHEN 단가*주문수량 >= 100000 THEN '최우수고객'
			WHEN 단가*주문수량 >= 10000 THEN '우수고객'
            ELSE '고객'
		END AS 고객분류
FROM 주문세부;

-- 마일리지 등급 부여 VIP, GOLD, SILVER, BRONZE
SELECT 고객번호
	,CASE WHEN 마일리지 >= 10000 THEN 'VIP'
		WHEN 마일리지 >= 5000 THEN 'GOLD'
		WHEN 마일리지 >= 1000 THEN 'SILVER'
		ELSE 'BRONZE'
	END AS 고객등급
FROM 고객;

SELECT * FROM 사원;
SELECT * FROM 부서;
SELECT 사원번호
		,CASE WHEN 부서번호 = 'A1' THEN '영업부'
			WHEN 부서번호 = 'A2' THEN '기획부'
            WHEN 부서번호 = 'A3' THEN '개발부'
            WHEN 부서번호 = 'A4' THEN '홍보부'
		END AS 부서명
FROM 사원;

SELECT 주문번호
	,CASE WHEN 발송일 >= 주문일 +2 THEN '일반배송'
		WHEN 발송일 >= 주문일 THEN '빠른배송'
        ELSE '배송대기'
	END AS 배송상태
FROM 주문;

# 연습4. 광역시, 특별시가 아닌 고객 중 마일리지 많은 고객 상위 3명이 누구일까??
SELECT 고객번호, 마일리지
FROM 고객
	WHERE 도시 NOT LIKE '%광역시' AND 도시 NOT LIKE '%특별시'
    ORDER BY 마일리지 DESC
    LIMIT 3;
    
SELECT SUM(마일리지) AS 마일리지합
FROM 고객
WHERE 도시 = '대전광역시';

SELECT COUNT(*)
	,COUNT(고객번호)
    ,COUNT(도시)
    ,COUNT(DISTINCT(지역))
FROM 고객;

SELECT 도시
	,SUM(마일리지)
	,AVG(마일리지)
    ,MIN(마일리지)
    ,MAX(마일리지)
FROM 고객
-- WHERE 도시 LIKE '서울%';
GROUP BY 도시;

SELECT 담당자직위
	,도시
	,COUNT(마일리지)
    ,SUM(마일리지)
    ,AVG(마일리지)
FROM 고객
GROUP BY 담당자직위, 도시
ORDER BY 담당자직위, 도시 DESC;

-- GROUP BY 조건 HAVING
-- 고객 - 도시별로 그룹 - 고객수ㅡ 평균마일리지, 고객수가 10 이상만 추출
SELECT 도시
    ,COUNT(고객번호) AS 고객수
    ,AVG(마일리지)
FROM 고객
GROUP BY 도시
HAVING AVG(마일리지) >= 1000;

-- 고객번호 t로 시작하는 고객을 도시별로 묶어 마일리지 합 출력, 단 1000점 이상만
SELECT 도시
	,sum(마일리지) as '마일리지 합'
FROM 고객
WHERE 고객번호 LIKE 't%'
GROUP BY 도시
HAVING SUM(마일리지) >= 1000;

-- 광역시 고객, 담당자 직위별로 최대 마일리지, 단, 1만점 이상 레코드만 출력
SELECT 담당자직위
	-- ,도시 (GROUP BY 대상이 아니기 떄문에 SELECT 할 수 없음
	,MAX(마일리지) AS '최대마일리지'
FROM 고객
WHERE 도시 LIKE '%광역시'
GROUP BY 담당자직위
WITH ROLLUP -- 총계 행이 추가
HAVING MAX(마일리지) >= 10000;

-- 연습1. 담당자 직위에 마케팅이 있는 고객의 담당자 직위, 도시별 고객수 출력
-- 단, 담당자 직위별 고객수와 전체 고객수도 출력
SELECT 담당자직위,
	도시,
    COUNT(고객번호) AS 고객수
FROM 고객
WHERE 담당자직위 LIKE '%마케팅%'
GROUP BY 담당자직위, 도시 WITH ROLLUP;

-- 연습2. 제품 주문년도별 주문건수 출력

-- 연습3. 