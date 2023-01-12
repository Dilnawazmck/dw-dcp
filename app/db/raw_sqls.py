GET_TOP_WORDS_IN_SURVEY_SQL = """
Select {group_by}, STRING_AGG(key, ', ' ORDER BY null) as words
from (Select {group_by},
             key,
             sum,
             row_number() over
                 (partition by {group_by} order by sum desc) as rn
      from (Select {group_by}, (js).key, sum((js).value::int) as sum
            from (select {group_by}, jsonb_each_text(top_words) as js from response r where r.survey_id = {survey_id} {filter_sql}) t
            {exclude_sql} group by {group_by}, (js).key) o) o2
where rn <= {top_n}
group by {group_by}
"""

GET_COMMENTS_COUNT_PER_GROUP_SQL = """
with v1 as (
with cte as
(
    select {group_by}, count(*) as count from response r where r.survey_id = {survey_id} {filter_sql}  group by {group_by}
)
select
{group_by},count,round((count/cast((select sum(count) from cte ) as float))*100 ) mention_score
from cte
)
select {group_by},count,mention_score,
case when mention_score {mention_type} ((select max(mention_score) from v1) +(select min(mention_score) from v1))/2 then 0 else 1 end sortorder
from v1 order by sortorder ,mention_score {order_by},count desc

"""

GET_SURVEY_RESPONSES = """
Select r.id, r.topic_id, r.practice_id, r.question_id, r.answer, r.answer_lang, r.translated_en_answer, r.filter_json,
case when usc.id is not null then True else False end as is_saved, {order_by}, usc.folder_name,
r.sentiment_id,r.sentiment_score
from response r {user_saved_comment_join_type} user_saved_comment usc
on (r.id = usc.response_id and usc.user_id = {user_id})
where r.survey_id = {survey_id} {filter_sql} {folder_name}
order by {order_by} desc,r.id  LIMIT {limit} OFFSET {offset}
"""

GET_TOTAL_COMMENTS_WITH_FILTER = """
Select count(r.id) as count
from response r {user_saved_comment_join}
where r.survey_id = {survey_id} {filter_sql}
"""

GET_WORDCLOUD_WITH_FILTER_SQL = """
With v1 as (select jsonb_each_text(top_words) as js from response r where r.survey_id = {survey_id} {filter_sql}),
     v2 as (Select (js).key as word, sum((js).value::int) as count from v1 {exclude_sql} group by (js).key)
select * from v2 order by count desc LIMIT {limit}
"""


GET_CLIENTS_AND_SURVEYS_SQL = """
select cl.id, cl.name, cl.surveys
from (
         select c.id,
                c.name,
                (select json_agg(surveys)
                 from (
                          select id, name, confirmit_pid, type, filters
                          from survey
                          where client_id = c.id
                      ) surveys
                ) as surveys
         from client as c) cl
"""

GET_RESPONSE_EXPORT_SQL = """
select q.name,
r.answer,
r.translated_en_answer,
p.name,
t.name,
array_to_string(Array(select jsonb_object_keys(r.top_words)), ',') as "top_words",
filter_json,
utr.topic as custom_topic,
case when usc.id is not null then True else False end as is_saved_comment,
folder_name,
s.name as sentiment
from response r
inner join question as q on q.id = r.question_id
inner join practice as p on p.id = r.practice_id
inner join topic as t on t.id = r.topic_id
left join user_topics_response utr on utr.user_id={user_id} and utr.response_id=r.id
left join user_saved_comment usc on usc.user_id={user_id} and usc.response_id=r.id
left join sentiment s on s.id= r.sentiment_id
where r.survey_id = {survey_id} {filter_sql} order by r.id asc
"""

GET_SAVED_RESPONSE_EXPORT_SQL = """
select q.name,
r.answer,
r.translated_en_answer,
p.name,
t.name,
array_to_string(Array(select jsonb_object_keys(r.top_words)), ',') as "top_words",
filter_json,
utr.topic as custom_topic,
case when usc.id is not null then True else False end as is_saved_comment,
folder_name,
s.name as sentiment
from response r
inner join user_saved_comment usc on r.id = usc.response_id
inner join question as q on q.id = r.question_id
inner join practice as p on p.id = r.practice_id
inner join topic as t on t.id = r.topic_id
left join user_topics_response utr on utr.user_id={user_id} and utr.response_id=r.id
left join sentiment s on s.id= r.sentiment_id
where r.survey_id = {survey_id} {filter_sql} and usc.user_id={user_id} order by r.id asc
"""

GET_SURVEY_FILTER_SQL = """
select filters, Array(select jsonb_object_keys(filters)) as filter_cols from survey where id = {survey_id}
"""

GET_USERS = """
select u.id, full_name, email, r.name as "role_name"
from public.user as u
inner join role as r on r.id = u.role_id
where u.is_deleted = false
"""

GET_USER_SURVEY_SQL = """
select cl.id, cl.name, cl.surveys
from (
         select c.id,
                c.name,
                (select json_agg(surveys)
                 from (
                          select s.id, s.name, confirmit_pid, type, filters
                          from user_survey as u
                          inner join survey as s on s.id = u.survey_id
                          where u.user_id = {user_id} and s.client_id = c.id
                          group by 1
                      ) surveys
                ) as surveys
         from client as c
         join survey s2 on (c.id=s2.client_id)
         join user_survey us on us.survey_id = s2.id
         where us.user_id = {user_id}
         group by 1
) cl

"""

GET_USER_ROLES_SURVEY = """
select count(1) from public.user usr
join role r on usr.role_id = r.id
join user_survey us on usr.id = us.user_id
where usr.email = '{user_email}' and us.survey_id = {survey_id}
"""

GET_USER_ROLES_SURVEY_RESPONSE = """
select count(1) from public.user usr
join role r on usr.role_id = r.id
join user_survey us on usr.id = us.user_id
join response re on re.survey_id = us.survey_id
where usr.email = '{user_email}' and re.id = {response_id}
"""

GET_FILTER_SUMMARY_DEMOS = """
with V1 as (
select  ( jsonb_each_text(filters)) as js,filters from survey where id={survey_id}
), v2 as
( select (js).key as key,
 (select  json_extract_path((js).value::json,'display_name')) as val,
 (select  json_extract_path((js).value::json,'options')) as val2 from V1 )
select  * from v2 where key in ('{key}')
"""

GET_COMMENTS_COUNT_PER_USER_TOPIC_GROUP_SQL = """
Select utr.topic, count(*) as count from user_topics_response utr
join response r on r.id = utr.response_id
where utr.user_id = {user_id} and r.survey_id = {survey_id} {filter_sql}
group by utr.topic
"""

GET_SENTIMENT_COUNT_BY_USER_TOPIC = """
select a.topic,
cast('['||STRING_AGG( '{sentiment_id}'||cast(a.sentiment_id as varchar(10))||'{sentiment_name}'||name||'{sentiment_count}'||coalesce(counts,0)||'{end_string}' ,',')||']' as json) as sentiment_data
from
(
select topic,id as sentiment_id,name from (
select topic from user_topics_response ut inner join response r on ut.response_id=r.id
where survey_id= {survey_id} and user_id={user_id} {filter_sql} group by topic)a cross join sentiment s  )a
left join
(
select topic,count(*) counts,sentiment_id from user_topics_response ut inner join response r on
ut.response_id=r.id where survey_id= {survey_id} and user_id={user_id} {filter_sql} group by topic,sentiment_id
)b on a.topic=b.topic and a.sentiment_id=b.sentiment_id
group by a.topic order by a.topic
"""

GET_TOP_WORDS_IN_SURVEY_BY_USER_TOPICS_SQL = """
Select topic, STRING_AGG(key, ', ' ORDER BY null) as words
from (Select topic,
             key,
             sum,
             row_number() over
                 (partition by topic order by sum desc) as rn
      from (Select topic, (js).key, sum((js).value::int) as sum
            from (select utr.topic, jsonb_each_text(r.top_words) as js from user_topics_response as utr
            join response r on r.id = utr.response_id
            where utr.user_id = {user_id} and r.survey_id = {survey_id} {filter_sql}) t
            {exclude_sql} group by topic, (js).key) o) o2
where rn <= {top_n}
group by topic
"""

GET_SURVEY_RESPONSES_WITH_USER_TOPICS = """
Select r.id, r.topic_id, r.practice_id, r.question_id, r.answer, r.answer_lang, r.translated_en_answer, r.filter_json,
case when usc.id is not null then True else False end as is_saved, utr.topic, r.sentiment_id, r.sentiment_score
from response r {user_saved_comment_join_type} user_saved_comment usc
on (r.id = usc.response_id and usc.user_id = {user_id})
join user_topics_response utr on r.id = utr.response_id
where utr.user_id= {user_id} and r.survey_id = {survey_id} {filter_sql}
order by utr.topic_similarity_score desc, r.id LIMIT {limit} OFFSET {offset}
"""

GET_MAX_RESPONSE_ID_BY_USER_TOPIC = """
select max(r.id) from response as r
inner join user_topics_response as utr on utr.response_id = r.id
where r.survey_id ={survey_id} and utr.user_id = {user_id}
"""

GET_SURVEY_ANSWERS = """
select id, answer from response {where_clause} order by id asc LIMIT {limit} OFFSET {offset}
"""

DELETE_USER_TOPICS_RESPONSE_BY_USERID_AND_SURVEYID = """
delete from user_topics_response
where exists (select id from response where survey_id={survey_id}) and user_id={user_id}
"""

DELETE_ALL_SAVED_COMMENTS = """
DELETE FROM user_saved_comment 
WHERE  user_id ={user_id} and response_id in (
select id from response where survey_id={survey_id} and type={survey_type} )
"""

GET_USER_SURVEY_FOLDER_LIST = """
SELECT folder_name,count(*) from response r inner join user_saved_comment usc on
r.id=usc.response_id
where usc.user_id={user_id} and r.survey_id={survey_id} and type={survey_type}
group by folder_name
"""


GET_SENTIMENTS_COUNTS = """

select {group_by},
Positive,Negative,Neutral,
case
 when positivecount+negativecount=0  then 0
 when (round(((positivecount-negativecount)/cast(positivecount+negativecount as float))*100) = -0  ) then 0 else round(((positivecount-negativecount)/cast(positivecount+negativecount as float))*100) end  sentiment_score
,cast('['||Sentiment_data||']' as json) sentiment_data
from (
with v1 as (
select a.{group_by},a.sentiment_id,name,coalesce(max(counts),0) counts from
(
select {group_by},s.id sentiment_id,s.name from response r cross join sentiment s
where survey_id={survey_id} {filter_sql} group by {group_by}, s.id,s.name )a
left join
(select {group_by},sentiment_id,count(*) counts from response r
 where survey_id={survey_id} {filter_sql} group by {group_by},sentiment_id)b
 on a.{group_by}=b.{group_by} and a.sentiment_id=b.sentiment_id
 group by a.{group_by},a.sentiment_id,name
)
select {group_by},
(select coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0)  from v1 where name='Neutral' and v1.{group_by}=v2.{group_by} ) Neutral ,
(select coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0)  from v1 where name='Positive' and v1.{group_by}=v2.{group_by} ) Positive ,
(select coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0)  from v1 where name='Negative' and v1.{group_by}=v2.{group_by} ) Negative ,
(select '{sentiment_id}'||cast(sentiment_id as varchar(10))||'{sentiment_name}'||name||'{sentiment_count}'||cast(coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0) as varchar(100))||'{end_string}' from v1 where name='Neutral' and v1.{group_by}=v2.{group_by} ) ||
(select ',{sentiment_id}'||cast(sentiment_id as varchar(10))||'{sentiment_name}'||name||'{sentiment_count}'||cast(coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0) as varchar(100))||'{end_string}' from v1 where name='Positive' and v1.{group_by}=v2.{group_by} )||
(select ',{sentiment_id}'||cast(sentiment_id as varchar(10))||'{sentiment_name}'||name||'{sentiment_count}'||cast(coalesce(round((counts/cast((select sum(counts) from v1 where v1.{group_by}=v2.{group_by} )as float))*100),0) as varchar(100))||'{end_string}'  from v1 where name='Negative' and {group_by}=v2.{group_by} )  Sentiment_data,
coalesce((select counts   from v1 where name='Neutral' and v1.{group_by}=v2.{group_by} ),0) Neutralcount,
coalesce((select counts  from v1 where name='Positive' and v1.{group_by}=v2.{group_by} ),0) Positivecount,
coalesce((select counts  from v1 where name='Negative' and {group_by}=v2.{group_by} ),0) Negativecount
from v1 as v2 group by {group_by})a  order by {sort_by}
"""

GET_SENTIMENT_BREAKDOWN = """
select
cast('['||STRING_AGG( '{sentiment_id}'||cast(b.sentiment_id as varchar(10))||'{sentiment_name}'||name||'{sentiment_count}'||coalesce(counts,0)||'{end_string}' ,',')||']' as json) as sentiment_data
from
(select s.id as sentiment_id,s.name,counts from sentiment s left join (
select sentiment_id,count(*) counts from response r
where survey_id={survey_id} {filter_sql} and
sentiment_id is not null group by sentiment_id )a on s.id=a.sentiment_id)b
"""

GET_SENTIMENT_WISE_DEMOGRAPHIC_SCORES="""
select * from (
with cte as (
	select	
((jsonb_each_text(filter_json))).key as jkey,
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id
from response r where r.survey_id={survey_id} {filter_sql} )
select jkey demo ,demo_value,count(*) nsize, count(*) over () totaldemos,
round((sum(case when sentiment_id=1 then 1 else 0 end )/(count(*)::real))*100) neutral,
round((sum(case when sentiment_id=2 then 1 else 0 end )/(count(*)::real))*100) positive,
round((sum(case when sentiment_id=3 then 1 else 0 end )/(count(*)::real))*100) negative
from cte  {demographic}
group by demo_value ,jkey having count(*) {nsize}
order by {sentiment} ,demo_value offset {skip} limit {limit} )v1
inner join 
(
with V1 as (
select  ( jsonb_each_text(filters)) as js,filters from survey where id={survey_id}
), v2 as
( select (js).key as jkey,
(select  json_extract_path((js).value::json,'display_name')) as demo_text,
(select  json_extract_path((js).value::json,'options')) as val2 from V1 )
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text,
demo_text from v2
)v2 on v1.demo_value=v2.option_code
order by {sentiment} ,demo_value 
"""

GET_SWD_POP_DATA="""
select a.demo_value,
COALESCE(STRING_AGG(case when practice_sentiment_id=1  then practice end,','),'') practice_neutral,
COALESCE(STRING_AGG(case when practice_sentiment_id=2 then practice end,','),'') practice_positive,
COALESCE(STRING_AGG(case when practice_sentiment_id=3 then practice end,','),'') practice_negative,
COALESCE(STRING_AGG(case when topic_sentiment_id=1 then topic end,','),'') topic_neutral,
COALESCE(STRING_AGG(case when topic_sentiment_id=2 then topic end,','),'') topic_positive,
COALESCE(STRING_AGG(case when topic_sentiment_id=3 then topic end,','),'') topic_negative
from 
(
with cte as (
select distinct ((jsonb_each_text(filter_json))).value as demo_value
from response r where r.survey_id={survey_id} {filter_sql}   
)
select demo_value,s.id sentiment_id from cte cross join  sentiment s where demo_value in {demographic}
)a 
left join 
(
	select demo_value,practice_sentiment_id,
	STRING_AGG( practice_name||'::'||counts ,',' order by counts desc,practice_name) Practice
	from (
		with cte as (
		select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,practice_id
		from response r where r.survey_id={survey_id} {filter_sql}  
		)select demo_value,p.name practice_name,sentiment_id practice_sentiment_id,count(*)counts,
		row_number() over ( partition by demo_value,sentiment_id order by count(*) desc )rown
		from cte c inner join practice p on c.practice_id=p.id  where demo_value in {demographic}
		group by demo_value,p.name,sentiment_id	
	)a 
	where rown<={limit} 
	group by demo_value,practice_sentiment_id
)b on a.demo_value=b.demo_value and a.sentiment_id=b.practice_sentiment_id
left join
(	
	select demo_value,topic_sentiment_id,
	STRING_AGG( topic_name||'::'||counts ,',' order by counts desc,topic_name) topic
	from (
	with cte as (
	select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id topic_sentiment_id,topic_id
	from response r where r.survey_id={survey_id} {filter_sql} 
	)select demo_value,t.name topic_name,topic_sentiment_id,count(*)counts,
		row_number() over ( partition by demo_value,topic_sentiment_id order by count(*) desc )rown
		from cte c inner join topic t on c.topic_id=t.id  where demo_value in {demographic}
	group by demo_value,t.name,topic_sentiment_id
	)a 
	where rown<={limit} 
group by demo_value,topic_sentiment_id
)c 
	on 
	a.demo_value=c.demo_value and 
	a.sentiment_id=c.topic_sentiment_id
	group by a.demo_value
"""

GET_SWD_POP_DATA2="""
select
v1.demo_value,practice_neutral,topic_neutral,practice_positive,topic_positive,practice_negative,topic_negative
from (select 
demo_value,
 STRING_AGG(case when r_neutral<=5 then  name||'::'||Neutralcount end,',' order by Neutralcount desc,name  ) practice_neutral,
 STRING_AGG(case when r_positive<=5 then name||'::'||Positivecount end,',' order by Positivecount desc,name )practice_positive,
 STRING_AGG(case when r_negative<=5 then name||'::'||Negativecount   end,',' order by Positivecount desc,name ) practice_negative 
from (
with cte as (
select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,practice_id
from response r where r.survey_id={survey_id} {filter_sql}   
)
select demo_value,p.name,p.id,
sum(case when sentiment_id=1 then 1 else 0 end ) Neutralcount,
sum(case when sentiment_id=2 then 1 else 0 end ) Positivecount,
sum(case when sentiment_id=3 then 1 else 0 end ) Negativecount,
row_number() over (partition by demo_value order by sum(case when sentiment_id=1 then 1 else 0 end ) desc,name)r_neutral, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=2 then 1 else 0 end ) desc,name )r_positive, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=3 then 1 else 0 end ) desc,name )r_negative
from cte c inner join practice p on c.practice_id=p.id 
where demo_value in {demographic}
	group by demo_value,practice_id,p.name,p.id
)a group by demo_value )
v1
left join
(	
select 
demo_value,
 STRING_AGG(case when r_neutral<=5 then name||'::'||Neutralcount end,',' order by Neutralcount desc,name ) topic_neutral,
 STRING_AGG(case when r_positive<=5 then  name||'::'||Positivecount  end,',' order by Positivecount desc,name )topic_positive,
 STRING_AGG(case when r_negative<=5 then  name||'::'||Negativecount  end,',' order by Positivecount desc,name ) topic_negative 
from (
with cte as (
select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,topic_id
from response r where r.survey_id={survey_id} {filter_sql} 
)
select demo_value,p.name,p.id,
sum(case when sentiment_id=1 then 1 else 0 end ) Neutralcount,
sum(case when sentiment_id=2 then 1 else 0 end ) Positivecount,
sum(case when sentiment_id=3 then 1 else 0 end ) Negativecount,
row_number() over (partition by demo_value order by sum(case when sentiment_id=1 then 1 else 0 end ) desc,name)r_neutral, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=2 then 1 else 0 end ) desc,name )r_positive, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=3 then 1 else 0 end ) desc,name )r_negative
from cte c inner join topic p on c.topic_id=p.id 
where demo_value in {demographic} group by demo_value,topic_id,p.name,p.id
)a group by demo_value 
)v2 on v1.demo_value=v2.demo_value
"""


GET_SENTIMENT_WISE_DEMOGRAPHIC_POPUP_DATA="""
select
--cast('{option_code}'||v1.demo_value||'{sentiment_neutral}'||practice_neutral||'{topic_data}'||topic_neutral||'{sentiment_positive}'||practice_positive||'{topic_data}'||topic_positive||'{sentiment_negative}'||practice_negative||'{topic_data}'||topic_negative||']}}'||'{endoffile}' as json) option_data
v1.demo_value,practice_neutral,topic_neutral,practice_positive,topic_positive,practice_negative,topic_negative
from (select 
demo_value,
 STRING_AGG(case when r_neutral<=5 then '{practice_name}'||name||'{count}'||Neutralcount||'{endoffile}' end,',' order by Neutralcount,name desc) practice_neutral,
 STRING_AGG(case when r_positive<=5 then '{practice_name}'||name||'{count}'||Positivecount||'{endoffile}' end,',' order by Positivecount,name desc)practice_positive,
 STRING_AGG(case when r_negative<=5 then '{practice_name}'||name||'{count}'||Negativecount||'{endoffile}'  end,',' order by Positivecount,name desc) practice_negative 
from (
with cte as (
select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,practice_id
from response r where r.survey_id={survey_id} {filter_sql}  
)
select demo_value,p.name,p.id,
sum(case when sentiment_id=1 then 1 else 0 end ) Neutralcount,
sum(case when sentiment_id=2 then 1 else 0 end ) Positivecount,
sum(case when sentiment_id=3 then 1 else 0 end ) Negativecount,
row_number() over (partition by demo_value order by sum(case when sentiment_id=1 then 1 else 0 end ) desc)r_neutral, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=2 then 1 else 0 end ) desc)r_positive, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=3 then 1 else 0 end ) desc)r_negative
from cte c inner join practice p on c.practice_id=p.id 
where demo_value in {demographic}
	group by demo_value,practice_id,p.name,p.id
)a group by demo_value )
v1
left join
(	
select 
demo_value,
 STRING_AGG(case when r_neutral<=5 then '{topic_name}'||name||'{count}'||Neutralcount||'{endoffile}' end,',' order by Neutralcount,name desc) topic_neutral,
 STRING_AGG(case when r_positive<=5 then '{topic_name}'||name||'{count}'||Positivecount||'{endoffile}' end,',' order by Positivecount,name desc)topic_positive,
 STRING_AGG(case when r_negative<=5 then '{topic_name}'||name||'{count}'||Negativecount||'{endoffile}'  end,',' order by Positivecount,name desc) topic_negative 
from (
with cte as (
select ((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,topic_id
from response r where r.survey_id={survey_id} {filter_sql} 
)
select demo_value,p.name,p.id,
sum(case when sentiment_id=1 then 1 else 0 end ) Neutralcount,
sum(case when sentiment_id=2 then 1 else 0 end ) Positivecount,
sum(case when sentiment_id=3 then 1 else 0 end ) Negativecount,
row_number() over (partition by demo_value order by sum(case when sentiment_id=1 then 1 else 0 end ) desc)r_neutral, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=2 then 1 else 0 end ) desc)r_positive, 
row_number() over (partition by demo_value order by sum(case when sentiment_id=3 then 1 else 0 end ) desc)r_negative
from cte c inner join topic p on c.topic_id=p.id 
where demo_value in {demographic} group by demo_value,topic_id,p.name,p.id
)a group by demo_value 
)v2 on v1.demo_value=v2.demo_value
"""

GET_TOTAL_DEMOS_COUNT="""
with cte as (
select	((jsonb_each_text(filter_json))).key as jkey,
((jsonb_each_text(filter_json))).value as demo_value
from response r where r.survey_id={survey_id} {filter_sql} )
select COUNT(*) OVER () from cte {demographic} 
group by demo_value  having count(*) {nsize} limit 1	
"""

GET_SENTIMENT_WISE_DEMOGRAPHICS = """
select v1.jkey demo, demo_text,option_code,option_text,nsize,neutral,positive,negative,practice_data,topic_data,
(
with cte as (
	select	((jsonb_each_text(filter_json))).key as jkey,
((jsonb_each_text(filter_json))).value as demo_value
from response r where r.survey_id={survey_id} {filter_sql} )
	select COUNT(*) OVER () from cte {demographic} 
	group by demo_value  having count(*) {nsize} limit 1
	)Totaldemos
from (
with cte as (
	select	
((jsonb_each_text(filter_json))).key as jkey,
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id
from response r where r.survey_id={survey_id} {filter_sql} )
select jkey,demo_value,count(*) nsize,
round((sum(case when sentiment_id=1 then 1 else 0 end )/(count(*)::real))*100) neutral,
round((sum(case when sentiment_id=2 then 1 else 0 end )/(count(*)::real))*100) positive,
round((sum(case when sentiment_id=3 then 1 else 0 end )/(count(*)::real))*100) negative
from cte  {demographic}
group by demo_value ,jkey having count(*) {nsize}
order by {sentiment} ,demo_value offset {skip} limit {limit} )v1
inner join 
(
with V1 as (
select  ( jsonb_each_text(filters)) as js,filters from survey where id={survey_id}
), v2 as
( select (js).key as jkey,
(select  json_extract_path((js).value::json,'display_name')) as demo_text,
(select  json_extract_path((js).value::json,'options')) as val2 from V1 )
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text,
jkey,demo_text from v2
)v2 on v1.demo_value=v2.option_code
left join 
(
select c.demo_value,cast('['||STRING_AGG('{type_id}'||p.name||'{count}'||cast((counts) as varchar(10))||'{endoffile}',',')||']' as json )  practice_data from (
with cte as (
	select
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,practice_id
from response r where r.survey_id={survey_id} {filter_sql} )
select demo_value,practice_id,count(*) counts,row_number() over (partition by demo_value order by count(*) desc)r 
from cte group by demo_value,practice_id )c inner join practice p on c.practice_id=p.id  
where r<=5  group by demo_value
)v3 on v3.demo_value=v1.demo_value
left join 
(
select c.demo_value,cast('['||STRING_AGG('{topic_type_id}'||p.name||'{count}'||cast((counts) as varchar(10))||'{endoffile}',',')||']' as json )  topic_data from (
with cte as (
	select
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,topic_id
from response r where r.survey_id={survey_id} {filter_sql} )
select demo_value,topic_id,count(*) counts,row_number() over (partition by demo_value order by count(*) desc)r 
from cte group by demo_value,topic_id )c inner join topic p on c.topic_id=p.id  
where r<=5  group by demo_value
)v4 on v4.demo_value=v1.demo_value
order by {sentiment}
"""

GET_SENTIMENT_MENTION_MATRIX = """
select p.name as {table_name},nsize,sentiment_score,mention_score,top_mention_demo ,top_sentiment_demo from (
with cte as (
select
{group_by},sentiment_id,(select count(*) from response r where survey_id={survey_id} {filter_sql}) Totalcounts
from response r
where survey_id={survey_id} {filter_sql} ) 
select {group_by},count(*) nsize, 
case when max(Totalcounts)=0 then 0 else round((count(*)/max(Totalcounts)::decimal(18,2))*100) end mention_score,
case when (sum((case when sentiment_id=2 then 1 else 0 end ))+
sum((case when sentiment_id=3 then 1 else 0 end )))=0 then 0 else 
round(((sum((case when sentiment_id=2 then 1 else 0 end ))-sum((case when sentiment_id=3 then 1 else 0 end )))/
(sum((case when sentiment_id=2 then 1 else 0 end ))+
sum((case when sentiment_id=3 then 1 else 0 end )))::decimal(18,2))*100) end sentiment_score
from cte  group by {group_by} 
)a left join 
(
select {group_by}, cast('['||STRING_AGG('"'||option_text||'"',',')||']' as json)  top_mention_demo from (
select
row_number() over (partition by {group_by} order by mention_score desc) rn,{group_by},option_text,demo_option,mention_score from (
select a.{group_by},b.demo_option,round((demo_option_counts/(demo_counts)::decimal(18,2))*100) mention_score 
from (
with cte as (
	select
((jsonb_each_text(filter_json))).key as demo,{group_by}
from response r where r.survey_id={survey_id} {filter_sql} )
select {group_by},demo,count(*) demo_counts
from cte v group by demo, {group_by})a
inner join 
(
with cte as (
	select
((jsonb_each_text(filter_json))).key as demo,((jsonb_each_text(filter_json))).value as demo_option,
	{group_by}
from response r where r.survey_id={survey_id} {filter_sql})
select {group_by},demo,demo_option,count(*) demo_option_counts
from cte v group by demo,demo_option ,{group_by}
)b on a.{group_by}=b.{group_by} and a.demo=b.demo)final inner join 
(
with v1 as (
select  json_extract_path(((jsonb_each_text(filters))).value::json,'options')val2 from survey where id={survey_id}
)
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text
 from v1 
)final2 on final.demo_option=final2.option_code)final3
where rn<=5 group by {group_by})b 
on a.{group_by}=b.{group_by}
left join 
(
select {group_by},cast('['||STRING_AGG('"'||option_text||'"',',')||']' as json) top_sentiment_demo from (
select 
row_number() over (partition by {group_by} order by sentiment_score desc) rn,* from (
with cte as (
	select
((jsonb_each_text(filter_json))).key as demo,
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,{group_by}
from response r where r.survey_id={survey_id} {filter_sql} )
select {group_by},demo,demo_value,count(*) demo_counts, 
case when (sum((case when sentiment_id=2 then 1 else 0 end ))+
sum((case when sentiment_id=3 then 1 else 0 end )))=0 then 0 else
round(((sum((case when sentiment_id=2 then 1 else 0 end ))-sum((case when sentiment_id=3 then 1 else 0 end )))/
(sum((case when sentiment_id=2 then 1 else 0 end ))+
sum((case when sentiment_id=3 then 1 else 0 end )))::decimal(18,2))*100) end sentiment_score
from cte  group by demo,demo_value,{group_by})a)b inner join 
(with v1 as (
select  json_extract_path(((jsonb_each_text(filters))).value::json,'options')val2 from survey where id={survey_id}
)
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text
 from v1 )c on b.demo_value=c.option_code
where rn<=5 
group by {group_by}
)c on c.{group_by}=a.{group_by}
inner join {table_name} p on p.id=a.{group_by}

"""

GET_SENTIMENT_MENTION_MATRIX_POPUP="""
select (select  cast('['||STRING_AGG('"'||option_text||'"',',')||']' as json) top_sentiment_demo from (
select  option_text,
case when (positive+negative)=0 then 0 else (((positive-negative)/(positive+negative)::real)*100) end 
sentiment_score from
(with cte as (
	select
((jsonb_each_text(filter_json))).value as demo_value,sentiment_id,{group_by}
from response r where r.survey_id={survey_id} {filter_sql} and {group_by}={group_by_id} )
select demo_value,option_text,
sum(case when sentiment_id=2 then 1 else 0 end )positive,
sum(case when sentiment_id=3 then 1 else 0 end )negative
from cte c inner join 
 (with v1 as (
select  json_extract_path(((jsonb_each_text(filters))).value::json,'options')val2 from survey where id={survey_id}
)
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text
 from v1 )oc on c.demo_value=oc.option_code
	 group by c.{group_by},option_text,demo_value
 )a order by sentiment_score limit 5)a),
 (
 select
cast('['||STRING_AGG('"'||option_text||'"',',')||']' as json) top_mention_demo from (
select oc.option_text ,round((b.demo_value_count/a.totalcount::real)*100)mention_score from 
(
with cte as (
select ((jsonb_each_text(filter_json))).key demo
from response r where r.survey_id={survey_id} and {group_by}={group_by_id})
select demo,count(*) Totalcount from cte  group by demo)a 
inner join 
(
with cte as (
	select ((jsonb_each_text(filter_json))).key demo,
		((jsonb_each_text(filter_json))).value demo_value
from response r where r.survey_id={survey_id} and {group_by}={group_by_id})
select demo_value,demo,count(*) demo_value_count from cte group by demo_value,demo
)b on a.demo=b.demo
inner join 
(with v1 as (
select  json_extract_path(((jsonb_each_text(filters))).value::json,'options')val2 from survey where id={survey_id}
)
select cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text
 from v1)oc on b.demo_value=oc.option_code
order by mention_score desc limit 5
)a
 )
"""


GET_DEMOGRAPHIC_HEATMAP = """

create temp table tmp(demo text,demo_option text,{group_by} int, sentiment_id int );
insert into tmp
with cte as (
select
((jsonb_each_text(filter_json))).key as demo,
((jsonb_each_text(filter_json))).value as demo_option,
{group_by},sentiment_id
from response  r
where survey_id={survey_id} {filter_sql})
select demo,demo_option ,{group_by},sentiment_id from cte where demo_option in (
select distinct demo_option from cte where demo='{demographic}' order by demo_option
offset {skip} limit {limit}) and demo='{demographic}'
;

with cte as (
select demo,val,demo_option,option_text,{group_by},nsize,
case when (positive+negative=0) then 0 else round(((positive-negative)/cast((positive+negative) as float))*100) end sentiment_score,
round((nsize/cast(totalcomments as float))*100) mention_score from
(
with v1 as (
select * from tmp  )
select v_final.demo_option,
v_final.{group_by} ,count(*) nsize,
(select count(*) from v1 where demo_option=v_final.demo_option) totalcomments,
(select count(*) from v1 where v1.{group_by}=v_final.{group_by} and sentiment_id=2 and v1.demo_option=v_final.demo_option) positive,
(select count(*) from v1 where v1.{group_by}=v_final.{group_by} and sentiment_id=3 and v1.demo_option=v_final.demo_option) negative
from v1 v_final

group by v_final.demo_option,v_final.{group_by}
)a inner join (
with V1 as
(
    select  ( jsonb_each_text(filters)) as js,filters from survey where id={survey_id}
), v2 as
( select (js).key demo,
(select  json_extract_path((js).value::json,'display_name')) as val,
(select  json_extract_path((js).value::json,'options')) as val2 from V1 )
select demo,val, cast((json_array_elements(val2)->>'column_value') as text) as option_code,
json_array_elements(val2)->>'display_name' option_text from v2 where demo='{demographic}'

)b on a.demo_option = b.option_code
)
select
demo_option,option_text,
cast('['||STRING_AGG(cast({group_by} as varchar(1000)),',')||']' as json) {group_by}_list,
cast('['||STRING_AGG(cast(sentiment_score as text),',')||']' as json) sentiment_score,
cast('['||STRING_AGG(cast(mention_score as text),',')||']' as json) mention_score
from cte  c inner join {table_name} p on c.{group_by}=p.id where p.name not in ('Unclassified')
group by demo_option,option_text
"""

GET_COMMENTS_TO_CLASSIFY = """
select *,1 rownumber from (select
r.id, r.topic_id, r.practice_id, r.question_id, r.answer, r.answer_lang, r.translated_en_answer, r.filter_json,
case when usc.id is not null then True else False end as is_saved, usc.folder_name,
r.sentiment_id,r.sentiment_score
from response r left join user_saved_comment usc
on (r.id = usc.response_id and usc.user_id = {user_id}) 
where survey_id={survey_id} and length(answer)>{length} and answer_lang='en'  and
coalesce (is_practice_verified,'false')='false' and type ={response_type} and
practice_id in (
select id from practice where name='Unclassified' and type={practice_type}
) limit 3)a
union
select *,2 from (
select
r.id, r.topic_id, r.practice_id, r.question_id, r.answer, r.answer_lang, r.translated_en_answer, r.filter_json,
case when usc.id is not null then True else False end as is_saved, usc.folder_name,
r.sentiment_id,r.sentiment_score
from response r left join user_saved_comment usc
on (r.id = usc.response_id and usc.user_id = {user_id})
where survey_id={survey_id} and
length(answer)>{length} and type={response_type} and  answer_lang='en' and
coalesce (is_practice_verified,'false')='false' and
practice_id in (select id from practice where name<>'Unclassified' and type={practice_type})
order by practice_similarity_score
limit {total_limit}
)b 
union
select *,3 from (
select
r.id, r.topic_id, r.practice_id, r.question_id, r.answer, r.answer_lang, r.translated_en_answer, r.filter_json,
case when usc.id is not null then True else False end as is_saved, usc.folder_name,
r.sentiment_id,r.sentiment_score
from response r left join user_saved_comment usc
on (r.id = usc.response_id and usc.user_id = {user_id})
where survey_id={survey_id} and
length(answer)>{length} and type={response_type} and translated_en_answer is not null and
coalesce (is_practice_verified,'false')='false' and
practice_id in (select id from practice where name<>'Unclassified' and type={practice_type})
order by practice_similarity_score
)c 
order by rownumber
limit {total_limit}
"""

UPDATE_EXCLUDE_KEYWORDS = """
update exclude_keywords set
keyword=to_json(array{exclude_keyword})
where survey_id={survey_id} and user_id={user_id}
"""
