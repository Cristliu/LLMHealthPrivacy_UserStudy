from __future__ import division
import os
import pandas as pd
import numpy as np
from IPy import IP
# import requests
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from LLMHPri import models
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
np.set_printoptions(suppress=True)

from django.shortcuts import redirect
from django.http import HttpResponse
from .models import UserSession
from .models import Dialogue
from django.utils import timezone
from datetime import timedelta
import openai
from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv())
load_dotenv()
openai.api_base = "***Fill in openai's api_base here***"
openai.api_key = "****sk-Fill in openai's api_key here***" 

def get_completion_3_1(prompt,model="gpt-3.5-turbo"): 
    messages = [
        {"role": "user", "content": prompt}
                ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5, # this is the degree of randomness of the model's output
        # max_tokens = 250,
    )
    return response.choices[0].message["content"]

def get_completion_3_4(prompt,model="gpt-3.5-turbo"): #始终指向最新的3.5模型 #为用户生成进一步提问的建议
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=1, # this is the degree of randomness of the model's output
        # max_tokens = 250,
    )
    return response.choices[0].message["content"]


# Create your views here.
@csrf_exempt


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def encindexzh(request):
    return render(request, 'LLMHPri/encindexzh.html', locals())

def encindexen(request):
    return render(request, 'LLMHPri/encindexen.html', locals())

def latest(request):
    return render(request, 'LLMHPri/latest.html', locals())

def showMessageAlert(request):
    return render(request, 'LLMHPri/showMessageAlert.html')

def end_session(request, session_id):
    try:
        # 直接通过会话ID查找，因为前端已经传递了ID
        session = UserSession.objects.get(id=session_id)
        session.end_time = timezone.now()
        # 直接计算持续时间并以秒为单位保存
        if session.end_time and session.start_time:
            duration_seconds = (session.end_time - session.start_time).total_seconds()
            session.duration = duration_seconds  # 直接保存秒数
        session.save()
        # 删除与会话相关的对话历史
        Dialogue.objects.filter(session=session).delete()
        # 返回成功状态的JSON响应给前端
        return JsonResponse({'status': 'success', 'message': '咨询结束。\n请记住待会需要填入的编号: 【'+str(session.id)+'】!!!! 请点击确定进入问卷调查界面！'})
    except UserSession.DoesNotExist:
        # 如果找不到会话，返回错误信息
        return JsonResponse({'status': 'error', 'message': '会话未找到。'}, status=404)


def end_session_en(request, session_id):
    try:
        session = UserSession.objects.get(id=session_id)
        session.end_time = timezone.now()
        if session.end_time and session.start_time:
            duration_seconds = (session.end_time - session.start_time).total_seconds()
            session.duration = duration_seconds
        session.save()
        Dialogue.objects.filter(session=session).delete()
        return JsonResponse({'status': 'success', 'message': 'The consultation is over.\nPlease remember the number you will need to fill in later: ['+str(session.id)+']!!!! Click OK to enter the questionnaire survey page!'})
    except UserSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found.'}, status=404)


@csrf_exempt 
def dialogue(request):
    if request.method == 'POST':#只有通过index的post才会新建一个Session
        # 用户从index页面通过表单提交，生成token
        request.session['valid_token'] = True
        ip_address = get_client_ip(request)
        new_session = UserSession.objects.create(ip_address=ip_address)
        return render(request, 'LLMHPri/dialogue.html', {'user_session_id': new_session.id,'valid_token': True})
        
    else:# 直接访问dialogue页面，检查session中的token以及id对应的end_time是否为空
        ip_address = get_client_ip(request)
        existing_session = UserSession.objects.filter(ip_address=ip_address).exists()
        
        if existing_session:
            #判断这个id对应的end_time是否为None, 如果存在着id且end_time为None则说明这个id对应的会话还没有结束, 可以继续进行对话
            #如果end_time不为None则说明这个id对应的会话已经结束, 不可以继续进行对话
            existing_session_end_time = UserSession.objects.filter(ip_address=ip_address).values('end_time').last()
            if existing_session_end_time['end_time'] == None:
                new_session = UserSession.objects.create(ip_address=ip_address)
                return render(request, 'LLMHPri/dialogue.html', {'user_session_id': new_session.id,'valid_token': True})
            else:
                return render(request, 'LLMHPri/showMessageAlert.html', {'message': '您不符合条件或已达最大参与次数，祝您健康快乐！'})
        else:
            return render(request, 'LLMHPri/showMessageAlert.html', {'message': '请先阅读并同意知情同意书'})

def survey(request):
    if request.method == 'POST':
        # 用户从index页面通过表单提交，生成token
        request.session['valid_token'] = True
        session_id = request.POST.get('session_id')
        # print(session_id)
        
        #不用验证，通过结束咨询的方式肯定是合法的访问
        if session_id:
            return render(request, 'LLMHPri/survey.html', {'user_session_id': session_id,'valid_token': True})
        else:
            return render(request, 'LLMHPri/showMessageAlert.html', {'message': '出错啦，请联系发布者'})
    
    else:#不允许用户通过url直接访问这个页面，也即只能通过跳转访问
        return render(request, 'LLMHPri/showMessageAlert.html', {'message': '请先完成咨询过程或通过结束咨询按钮跳转'})

@csrf_exempt 
def consultdia(request):
    if request.method == 'POST':#只有通过index的post才会新建一个Session
        # 用户从index页面通过表单提交，生成token
        request.session['valid_token'] = True
        ip_address = get_client_ip(request)
        
        new_session = UserSession.objects.create(ip_address=ip_address)
        return render(request, 'LLMHPri/consultDia.html', {'user_session_id': new_session.id,'valid_token': True})
        
    else:# 直接访问dialogue页面，检查session中的token以及id对应的end_time是否为空
        ip_address = get_client_ip(request)
        existing_session = UserSession.objects.filter(ip_address=ip_address).exists()
        
        if existing_session:
            existing_session_end_time = UserSession.objects.filter(ip_address=ip_address).values('end_time').last()
            if existing_session_end_time['end_time'] == None:
                new_session = UserSession.objects.create(ip_address=ip_address)
                return render(request, 'LLMHPri/consultDia.html', {'user_session_id': new_session.id,'valid_token': True})
            else:
                return render(request, 'LLMHPri/showMessageAlert.html', {'message': 'You do not meet the criteria or have reached the maximum number of participations. Wishing you health and happiness!'})
        else:
            return render(request, 'LLMHPri/showMessageAlert.html', {'message': 'Please read and agree to the informed consent form first.'})


def qnsurvey(request):
    if request.method == 'POST':
        # 用户从index页面通过表单提交，生成token
        request.session['valid_token'] = True
        session_id = request.POST.get('session_id')
        # print(session_id)
        #不用验证，通过结束咨询的方式肯定是合法的访问
        if session_id:
            return render(request, 'LLMHPri/QNSurvey.html', {'user_session_id': session_id,'valid_token': True})
        else:
            return render(request, 'LLMHPri/showMessageAlert.html', {'message': 'Oops, something went wrong. Please contact the publisher.'})
    
    else:#不允许用户通过url直接访问这个页面，也即只能通过跳转访问
        return render(request, 'LLMHPri/showMessageAlert.html', {'message': 'Please complete the consultation process first or jump through the End Consultation button.'})


@csrf_exempt 
def send_message(request,session_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        provideInfo = data.get('provideInfo', '')

        session_dialogues = Dialogue.objects.filter(session_id=session_id)
        history_context = "\n".join([f"{d.sender}: {d.message}" for d in session_dialogues])

        if provideInfo == 'yes':
            age = data.get('age', '')
            gender = data.get('gender', '')
            occupation = data.get('occupation', '')
            prompt = f"""
            As an experienced and trustworthy healthcare professional, your task is to provide reliable and impressive answers to user inquiries. Please ensure:
            Consider the conversation history (if any) as: "{history_context}", to provide connected answers.
            But don't print the conversation history in your response.
            Moreover, don't repeat answers that have already been provided in the history conversation.
            The user's question this time is:"{user_message}".
            The user's age is "{age}", gender is "{gender}", and occupation or status is "{occupation}".
            Avoid irrelevant answers: For non-medical health-related questions, avoid answering and guide the discussion back to medical and health topics.
            For general medical or health knowledge questions, answer directly and concisely.
            For personal health inquiries from users, you must provide personalized and appropriate advice based on the information provided by the user, such as age, gender, and occupation.
            These advice include, but not limited to conventional medications, herbal remedies, naturopathic remedies or more innovative therapies.
            If the patient needs something prescribed, start by asking specific questions that center around details such as the patient's duration, allergy history, and past medical history.
            Always respond in Chinese, keeping the language clear, friendly, and easy to understand. Try to answer in points to increase organization.
            Ensure your response no more than 200 Chinese characters, avoiding the use of Markdown or rich text formats.
            Avoid specific phrases: Do not start with prefixes like 'Answer:' and do not directly mention 'innovative treatments' or similar terms.
            Never disclose that you are a "GPT" or an 'AI model' with limitations. Always behave as if you were a real doctor, and avoid suggesting that users 'consult with a healthcare professional'.
            Remember to provide personalized responses related to the user's basic information.
            """
            response = get_completion_3_1(prompt)
            # print("response: ", response)
            
        else:
            prompt = f"""
            As an experienced and trustworthy healthcare professional, your task is to provide reliable and impressive answers to user inquiries. Please ensure:
            Consider the conversation history (if any) as: "{history_context}", to provide connected answers.
            But don't print the conversation history in your response.
            Moreover, don't repeat answers that have already been provided in the history conversation.
            The user's question this time is:"{user_message}".
            Avoid irrelevant answers: For non-medical health-related questions, avoid answering and guide the discussion back to medical and health topics.
            For general medical or health knowledge questions, answer directly and concisely.
            For personal health inquiries from users, the advice provided include, but not limited to conventional medications, herbal remedies, naturopathic remedies or more innovative therapies.
            If the patient needs something prescribed, start by asking specific questions that center around details such as the patient's duration, allergy history, and past medical history.
            Always respond in Chinese, keeping the language clear, friendly, and easy to understand. Try to answer in points to increase organization.
            Ensure your response no more than 200 Chinese characters, avoiding the use of Markdown or rich text formats.
            Avoid specific phrases: Do not start with prefixes like 'Answer:' and do not directly mention 'innovative treatments' or similar terms.
            Never disclose that you are a "GPT" or an 'AI model' with limitations. Always behave as if you were a real doctor, and avoid suggesting that users 'consult with a healthcare professional'.
            Remember to ask questions and provide personalized responses for personal health inquiries from users.
            """

            response = get_completion_3_1(prompt)


        prompt2 = f"""
        You are an experienced and trustworthy GPT healthcare professional.
        Your task is to provide users with questions that they can continue to ask you also i.e. GPT Medical Experts. 
        Please ensure:
        Providing questions related to the context of the conversation for the user to ask further.
        The conversation history between the user and you is: "{history_context}".
        The user's question this time is: "{user_message}" and the your answer this time is: "{response}".
        Without using the prefix 'suggested follow-up question:', "User:", etc.
        Provide the question in Chinese, ensuring it does not exceed 30 Chinese characters.
        """

        suggestions = get_completion_3_4(prompt2)
        gpt_response = response
        gpt_suggestions = [f"{suggestions}"]

        try:
            # 通过会话ID找到当前的UserSession实例
            session = UserSession.objects.get(id=session_id)

            Dialogue.objects.create(session=session, sender="user", message=user_message)
            Dialogue.objects.create(session=session, sender="gpt", message=response)
            
            if provideInfo == 'yes':
                session.provided_info = True
                # session.age_group = age
                # session.gender = gender
                # session.occupation = occupation
            else:
                session.provided_info = False
         
            session.save()

        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)

        # 返回一个Json响应包含GPT的回复和预设提示词
        return JsonResponse({'message': gpt_response, 'suggestions': gpt_suggestions})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt 
def send_message_en(request,session_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        provideInfo = data.get('provideInfo', '')

        random_number = session_id % 2
        judge10_numer = session_id % 10

        session_dialogues = Dialogue.objects.filter(session_id=session_id)
        history_context = "\n".join([f"{d.sender}: {d.message}" for d in session_dialogues])

        if provideInfo == 'yes':
            age = data.get('age', '')
            gender = data.get('gender', '')
            occupation = data.get('occupation', '')
            prompt = f"""
            As an experienced and trustworthy healthcare professional, your task is to provide reliable and impressive answers to user inquiries. Please ensure:
            Consider the conversation history (if any) as: "{history_context}", to provide connected answers.
            But don't print the conversation history in your response.
            Moreover, don't repeat answers that have already been provided in the history conversation.
            The user's question this time is:"{user_message}".
            The user's age is "{age}", gender is "{gender}", and occupation or status is "{occupation}".
            Avoid irrelevant answers: For non-medical health-related questions, avoid answering and guide the discussion back to medical and health topics.
            For general medical or health knowledge questions, answer directly and concisely.
            For personal health inquiries from users, you must provide personalized and appropriate advice based on the information provided by the user, such as age, gender, and occupation.
            These advice include, but not limited to conventional medications, herbal remedies, naturopathic remedies or more innovative therapies.
            If the patient needs something prescribed, start by asking specific questions that center around details such as the patient's duration, allergy history, and past medical history.
            Always respond in English, keeping the language clear, friendly, and easy to understand. Try to answer in points to increase organization.
            Ensure your response no more than 150 English words, avoiding the use of Markdown or rich text formats.
            Avoid specific phrases: Do not start with prefixes like 'Answer:' and do not directly mention 'innovative treatments' or similar terms.
            Never disclose that you are a "GPT" or an 'AI model' with limitations. Always behave as if you were a real doctor, and avoid suggesting that users 'consult with a healthcare professional'.
            Remember to provide personalized responses related to the user's basic information.
            """
            response = get_completion_3_1(prompt)
            
        else:
            prompt = f"""
            As an experienced and trustworthy healthcare professional, your task is to provide reliable and impressive answers to user inquiries. Please ensure:
            Consider the conversation history (if any) as: "{history_context}", to provide connected answers.
            But don't print the conversation history in your response.
            Moreover, don't repeat answers that have already been provided in the history conversation.
            The user's question this time is:"{user_message}".
            Avoid irrelevant answers: For non-medical health-related questions, avoid answering and guide the discussion back to medical and health topics.
            For general medical or health knowledge questions, answer directly and concisely.
            For personal health inquiries from users, the advice provided include, but not limited to conventional medications, herbal remedies, naturopathic remedies or more innovative therapies.
            If the patient needs something prescribed, start by asking specific questions that center around details such as the patient's duration, allergy history, and past medical history.
            Always respond in English, keeping the language clear, friendly, and easy to understand. Try to answer in points to increase organization.
            Ensure your response no more than 150 English words, avoiding the use of Markdown or rich text formats.
            Avoid specific phrases: Do not start with prefixes like 'Answer:' and do not directly mention 'innovative treatments' or similar terms.
            Never disclose that you are a "GPT" or an 'AI model' with limitations. Always behave as if you were a real doctor, and avoid suggesting that users 'consult with a healthcare professional'.
            Remember to ask questions and provide personalized responses for personal health inquiries from users.
            """

            response = get_completion_3_1(prompt)
        prompt2 = f"""
        You are an experienced and trustworthy GPT healthcare professional.
        Your task is to provide users with questions that they can continue to ask you also i.e. GPT Medical Experts. 
        Please ensure:
        Providing questions related to the context of the conversation for the user to ask further.
        The conversation history between the user and you is: "{history_context}".
        The user's question this time is: "{user_message}" and the your answer this time is: "{response}".
        Without using the prefix 'suggested follow-up question:', "User:", etc.
        Provide the question in English, ensuring it does not exceed 30 English words.
        """


        suggestions = get_completion_3_4(prompt2)

        gpt_response = response
        gpt_suggestions = [f"{suggestions}"]

        try:
            session = UserSession.objects.get(id=session_id)

            Dialogue.objects.create(session=session, sender="user", message=user_message)
            Dialogue.objects.create(session=session, sender="gpt", message=response)
            
            if provideInfo == 'yes':
                session.provided_info = True
            else:
                session.provided_info = False
         
            session.save()

        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)

        return JsonResponse({'message': gpt_response, 'suggestions': gpt_suggestions})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)