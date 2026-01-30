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

SELECT 주문번호 FROM 주문세부
SELECT 제품번호
	, FORMAT(단가,0) AS 단가
    , 주문수량
    , 할인율
    , FORMAT(주문수량*단가*(1-할인율),0) AS 주문금액
FROM 주문세부;
