from django.shortcuts import render
from .models import Main_table,Display_score
from .forms import GetDateForm
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView
from .services import get_defects
import time
import requests
import json
import datetime

def get_date(request):
	if request.method=='POST':
		date=request.post['date']
		print(date)
	return render(request, "index.html",{})


		
def defects_raised(comments):
    defect_set={}
    for i in comments:
        if i["defectRaised"]:
            user_name=i["user"]["userName"]
            points=1
            try:
                if i["metrics"]["rank"]["value"]== "Minor":
                    points= points + 0.5
                elif i["metrics"]["rank"]["value"]== "Major":
                    points= points + 1
            except KeyError:
                pass
            if user_name in defect_set.keys():
                defect_set[user_name]=defect_set[user_name] + points
            else:
                defect_set[user_name]= points
    return defect_set 



def comments_scoring_1(comment_data):
    comments_set={}
    for i in comment_data:
      user_name=i["user"]["userName"]
      if user_name in comments_set.keys():
            comments_set[user_name]=comments_set[user_name]+i["message"]
      else:
        comments_set[user_name]=i["message"]
    users=comments_set.keys()
    for i in users:
        score = 0
        indent = comments_set[i].count("indent")
        indent1 = comments_set[i].count("Indent") + indent
        checklist=comments_set[i].count("checklist")
        checklist1 = comments_set[i].count("Checklist") + checklist
        if indent1 >2:
            score=score - 1
        if checklist1 >=2:
            score=score + 1
        comments_set[i]=score
    return comments_set




def testcase_file_ids(review_data):
    test_ids=[]
    review_items=review_data["reviewItems"]["reviewItem"]
    for i in review_items:
        if "test" in i["expandedRevisions"][0]["path"]:
            test_ids.append(i["permId"]["id"])
    return test_ids




def comments_scoring_based_on_test_files(comment_data,test_ids):
    comments_set={}
    for i in comment_data:
        if i["reviewItemId"]["id"] in test_ids:
            user_name=i["user"]["userName"]
            if user_name in comments_set.keys():
                comments_set[user_name]=comments_set[user_name]+1
            else:
                comments_set[user_name]=1
    for i in comments_set.keys():
        comments_set[i]=comments_set[i]/3
    return comments_set




def calculate_total_score(dict_score,total_score_dict):
    for i in dict_score:
        user_id=i
        score=dict_score[i]
        if user_id in total_score_dict:
            total_score_dict[user_id]+=score
        else:
            total_score_dict[user_id]=score
    return total_score_dict





def get_score(review_id,authorization):
    url="https://crucible01.cerner.com/rest-service/reviews-v1/"+review_id+"/details"
    r=requests.get(url,auth=authorization,headers={'content-type':'application/json', 'accept':'application/json'})
    results=json.dumps(r.json(),indent=6)
    output=json.loads(results)
    comments=output["versionedComments"]["comments"]
    total_score_dict={}
    test_ids=testcase_file_ids(output)
    score_func=[defects_raised(comments),comments_scoring_1(comments),comments_scoring_based_on_test_files(comments,test_ids)]
    for i in score_func:
        total_score_dict=calculate_total_score(i,total_score_dict)
    print(total_score_dict)
    closed_datetime_str=output["closeDate"]
    closed_date_str=closed_datetime_str[0:10]
    closed_date=parse_date(closed_date_str)
    return total_score_dict,closed_date




def store_data(request):
	context = {}
	if request.method=="POST":
		authorization=("","")
		r=requests.get("https://crucible01.cerner.com/rest-service/reviews-v1/filter/details?states=Closed&fromDate=1606761000000&project=SYNAPSE-CR&states=Closed",auth=authorization,headers={'content-type':'application/json', 'accept':'application/json'})
		results=json.dumps(r.json(),indent=6)
		output=json.loads(results)
		all_reviews=output['detailedReviewData']
		all_review_ids=[]
		for i in all_reviews:
			id=i['permaId']['id']
			if id not in all_review_ids:
				all_review_ids.append(id)
		print(len(all_review_ids))
		print(all_review_ids)
		Main_table.objects.all().delete()
		for i in all_review_ids:
		    final_result=get_score(i,authorization)
		    store=Main_table(review_id=i,reviewers_score=final_result[0],review_closed_date=final_result[1])
		    store.save()
		all_data=Main_table.objects.all()
		context={"all_data":all_data}
		
	return render(request, "execute.html",context)



def calcluate_top_scorer(request):
	Main_table.objects.values('reviewers_score')
	date_form=GetDateForm()
	score_calculator_dict={}
	if request.method=="POST":
		date_form=GetDateForm(request.POST)
		if date_form.is_valid():
			print("this is the date form front end",date_form.cleaned_data)
			calculate_date=date_form.cleaned_data['my_date_field']
			reviewers_score=Main_table.objects.filter(review_closed_date__gte = calculate_date).values('reviewers_score')
			for i in reviewers_score.iterator():
				for j in i:
					new_dicty=i[j]
					for z in new_dicty:
						user_name=z
						score=new_dicty[z]
						if user_name not in score_calculator_dict:
							score_calculator_dict[user_name]=score
						else:
							score_calculator_dict[user_name]+=score
			print(score_calculator_dict)
			Display_score.objects.all().delete()
			for i in score_calculator_dict:
				store=Display_score(employee_id=i,score=score_calculator_dict[i])
				store.save()


	context={
	"form":date_form
	}


	return render(request, "index.html", context)




def display_score(request):
	ordered_set_of_score=Display_score.objects.all().order_by('-score')
	context={"all_data":ordered_set_of_score}

	return render(request, "table.html", context)



