from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.conf import settings
from django.core.mail import EmailMessage
import smtplib
from email.message import EmailMessage
import imghdr
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re
from account.models import User
from jobapp.forms import *
from jobapp.models import *
from jobapp.permission import *


User = get_user_model()

def resumeMaker_view(request):
    print('\n YaY')
    if request.method == "POST":
        global template_loc, tmp, img_h, data
        data = request.POST

        template_loc = "images/ResumeSite.jpg"
        tmp = Image.open(template_loc)  # Cft = Certificate
        linedrw = ImageDraw.Draw(tmp)
        s_size = 15
        m_size = 22

        # Drawing Name ----------------------------------------------------------
        xCrnt, yCrnt = drawtext(data['name'], 50, 35, 41, 30, (255, 255, 255), path="fonts/Righteous-Regular.ttf")

        # Drawing Contacts 478 176 ----------------------------------------------
        font = ImageFont.truetype('arial.ttf', s_size)
        img_h = font.getsize('I')[1]
        xCrnt = 478
        yCrnt = 180
        drawimg('images/email1.png',480,yCrnt)
        xCrnt, yCrnt = drawtext(data['email'], s_size, 25, 510, yCrnt+2, (0, 0, 0))

        drawimg('images/phone1.png', 480, yCrnt+10)
        xCrnt, yCrnt = drawtext(data['number'], s_size, 25, 510, yCrnt+12, (0, 0, 0))

        drawimg('images/maps1.png', 480, yCrnt + 17)
        xCrnt, yCrnt = drawtext(data['address'], s_size, 25, 510, yCrnt+12, (0, 0, 0)) #(53, 63, 88)

        drawimg('images/linkedin1.png', 480, yCrnt + 13)
        xCrnt, yCrnt = drawtext(data['linkedin'], s_size, 25, 510, yCrnt+12, (0, 0, 0))


        # Drawing skills
        xCrnt, yCrnt = drawtext("SKILLS", m_size, 20, 490, yCrnt + 20, (0, 0, 0))
        linedrw.line([(xCrnt, yCrnt+10), (xCrnt+50, yCrnt+10)], fill=(97, 115, 159))
        yCrnt += 5
        temp = re.split(",",data['skills'])
        for i in temp:
            xCrnt, yCrnt = drawtext(i, s_size, 25, 490, yCrnt + 8, (0, 0, 0))


        # Drawing Education
        xCrnt, yCrnt = drawtext("EDUCATION", m_size, 20, 490, yCrnt + 20, (0, 0, 0))
        linedrw.line([(xCrnt, yCrnt + 10), (xCrnt + 50, yCrnt + 10)], fill=(97, 115, 159))
        yCrnt += 8
        for i in range(1, 5):
            s = 'school'+ " " + str(i)
            y = 'year' + " " + str(i)
            m = 'marks'+ " " + str(i)

            if(data[s] != ''):
                xCrnt, yCrnt = drawtext(data[s], s_size+3, 20, 490, yCrnt + 18, (0, 0, 0))
                xCrnt, yCrnt = drawtext(data[y] + " / " + data[m], s_size, 25, 490, yCrnt + 5, (0, 0, 0))

        # Drawing Awards
        yCrnt += 5
        xCrnt, yCrnt = drawtext("AWARDS", m_size, 25, xCrnt, yCrnt + 20, (0, 0, 0))
        linedrw.line([(xCrnt, yCrnt + 10), (xCrnt + 50, yCrnt + 10)], fill=(97, 115, 159))
        awards = re.split("\*", data["awards"])
        for i in range(0, len(awards)):
            xCrnt, yCrnt = drawtext(awards[i], s_size, 30, xCrnt, yCrnt + 8, (0, 0, 0))

        # Drawing Summary
        xCrnt = 41
        yCrnt = 180
        xCrnt, yCrnt = drawtext("SUMMARY", m_size, 25, xCrnt, yCrnt, (0, 0, 0))
        linedrw.line([(xCrnt, yCrnt + 10), (xCrnt + 50, yCrnt + 10)], fill=(97, 115, 159))
        xCrnt, yCrnt = drawtext(data['summary'], s_size, 60, xCrnt, yCrnt + 20, (0, 0, 0))

        # Drawing Experience
        xCrnt, yCrnt = drawtext("EXPERIENCE", m_size, 25, xCrnt, yCrnt + 20, (0, 0, 0))
        linedrw.line([(xCrnt, yCrnt + 10), (xCrnt + 50, yCrnt + 10)], fill=(97, 115, 159))
        experience = re.split("\#|\*", data["experience"])

        for i in range(0, len(experience)):
            xCrnt = 41
            t = 15
            if i == 0:
                t = 25
            if (i % 2) != 0:  # Even
                if i == len(experience)-1:
                    xCrnt, yCrnt = drawtext(experience[i], s_size + 4, 50, xCrnt, yCrnt + t, (0, 0, 0), 1)
                else:
                    xCrnt, yCrnt = drawtext(experience[i], s_size + 4, 50, xCrnt, yCrnt + t, (0, 0, 0))
            else:
                if i == len(experience)-1:
                    xCrnt, yCrnt = drawtext(experience[i], s_size, 50, xCrnt, yCrnt + 6, (0, 0, 0), 1)
                else:
                    xCrnt, yCrnt = drawtext(experience[i], s_size, 50, xCrnt, yCrnt + 6, (0, 0, 0))

        return render(request, "jobapp/file_sent.html")
    return render(request, "jobapp/builder.html")


def drawimg(loc1, x, y):
    img = Image.open(loc1).resize((img_h + 8, img_h + 8)).convert("L")
    tmp.paste(img, (x, y))


def drawtext(text,size,nwords,x,y, fontcolor, print=0,path='arial.ttf'):

    # --------------------- Making the Resume ---------------------
    # Wrapping the text
    draw = ImageDraw.Draw(tmp)
    font = ImageFont.truetype(path, size)
    lines = textwrap.wrap(text, nwords)

    for line in lines:
        w, h = font.getsize(line)
        draw.text(xy=(x, y), text=line, fill=fontcolor, font=font)
        y = y + h + 6

    if print:
        tmp.show()
        tmp.save('user_resume/Resume_' + str(data["name"].replace(" ", "")) + '.pdf')

        #  Variable Initialization
        filename = 'user_resume/Resume_' + str(data["name"].replace(" ", "")) + '.pdf'
        gmail_id = settings.EMAIL_HOST_USER
        gmail_subject = 'Resume: By Dignizant Jobs'
        gmail_content = """
Hello <name>, 
It's wonderful that you chose Our service to make your resume. Good luck for your interview.
        
Regards,
Dignizant Jobs
"""

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()  # Traffic encryption
        s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        msg = EmailMessage()
        msg['Subject'] = gmail_subject
        msg['From'] = gmail_id
        msg['To'] = data['email']
        gmail_content = gmail_content.replace("<name>", data['name'])
        msg.set_content(gmail_content)

        # Attaching the Poster
        f = open(filename, 'rb')
        fdata = f.read()
        # fname = 'images/' + CertificateFileName
        fname = 'Resume_' + str(data["name"].replace(" ", "")) + '.pdf'

        file_type = imghdr.what(f.name)
        msg.add_attachment(fdata, maintype='application', subtype='octet-stream', filename=fname)
        s.send_message(msg)
        s.quit()

    return x, y
def about_view(request):

 return render(request, 'jobapp/about.html')



def resume_view (request):

     return render(request,'jobapp/resume.html')



def home_view(request):

    published_jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    jobs = published_jobs.filter(is_closed=False)
    total_candidates = User.objects.filter(role='employee').count()
    total_companies = User.objects.filter(role='employer').count()
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page',None)
    page_obj = paginator.get_page(page_number)

    if request.is_ajax():
        job_lists=[]
        job_objects_list = page_obj.object_list.values()
        for job_list in job_objects_list:
            job_lists.append(job_list)
        

        next_page_number = None
        if page_obj.has_next():
            next_page_number = page_obj.next_page_number()

        prev_page_number = None       
        if page_obj.has_previous():
            prev_page_number = page_obj.previous_page_number()

        data={
            'job_lists':job_lists,
            'current_page_no':page_obj.number,
            'next_page_number':next_page_number,
            'no_of_page':paginator.num_pages,
            'prev_page_number':prev_page_number
        }    
        return JsonResponse(data)
    
    context = {

    'total_candidates': total_candidates,
    'total_companies': total_companies,
    'total_jobs': len(jobs),
    'total_completed_jobs':len(published_jobs.filter(is_closed=True)),
    'page_obj': page_obj
    }
    print('ok')
    return render(request, 'jobapp/index.html', context)


def job_list_View(request):
    """

    """
    job_list = Job.objects.filter(is_published=True,is_closed=False).order_by('-timestamp')
    paginator = Paginator(job_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {

        'page_obj': page_obj,


    }
    print(job_list)
    return render(request, 'jobapp/job-list.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def create_job_View(request):
    """
    Provide the ability to create job post
    """
    user = get_object_or_404(User, id=request.user.id)
    categories = Category.objects.all()  
    form = JobForm()
    if request.method == 'POST':
        
        form = JobForm(request.POST ,request.FILES)

    


        if form.is_valid():

            instance = form.save(commit=False)
            instance.user = user
            instance.save()
            # for save tags
            form.save_m2m()
            messages.success(
                    request, 'You are successfully posted your job! Please wait for review.')
            return redirect(reverse("jobapp:single-job", kwargs={
                                    'id': instance.id
                                    }))

    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'jobapp/post-job.html', context)


def single_job_view(request, id):
    """
    Provide the ability to view job details
    """

    job = get_object_or_404(Job, id=id)
    related_job_list = job.tags.similar_objects()

    paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        'page_obj': page_obj,
        'total': len(related_job_list)

    }
    return render(request, 'jobapp/job-single.html', context)


def search_result_view(request):
    """
        User can search job with multiple fields

    """

    job_list = Job.objects.order_by('-timestamp')

    # Keywords
    if 'job_title_or_company_name' in request.GET:
        job_title_or_company_name = request.GET['job_title_or_company_name']

        if job_title_or_company_name:
            job_list = job_list.filter(title__icontains=job_title_or_company_name) | job_list.filter(
                company_name__icontains=job_title_or_company_name)

    # location
    if 'location' in request.GET:
        location = request.GET['location']
        if location:
            job_list = job_list.filter(location__icontains=location)

    # Job Type
    if 'job_type' in request.GET:
        job_type = request.GET['job_type']
        if job_type:
            job_list = job_list.filter(job_type__iexact=job_type)

    # job_title_or_company_name = request.GET.get('text')
    # location = request.GET.get('location')
    # job_type = request.GET.get('type')

    #     job_list = Job.objects.all()
    #     job_list = job_list.filter(
    #         Q(job_type__iexact=job_type) |
    #         Q(title__icontains=job_title_or_company_name) |
    #         Q(location__icontains=location)
    #     ).distinct()

    # job_list = Job.objects.filter(job_type__iexact=job_type) | Job.objects.filter(
    #     location__icontains=location) | Job.objects.filter(title__icontains=text) | Job.objects.filter(company_name__icontains=text)

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {

        'page_obj': page_obj,

    }
    return render(request, 'jobapp/result.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def apply_job_view(request, id):

    form = JobApplyForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = Applicant.objects.filter(user=user, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                messages.success(
                    request, 'You have successfully applied for this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:

        messages.error(request, 'You already applied for the Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
def dashboard_view(request):
    """
    """
    jobs = []
    savedjobs = []
    appliedjobs = []
    total_applicants = {}
    if request.user.role == 'employer':

        jobs = Job.objects.filter(user=request.user.id)
        for job in jobs:
            count = Applicant.objects.filter(job=job.id).count()
            total_applicants[job.id] = count

    if request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user.id)
        appliedjobs = Applicant.objects.filter(user=request.user.id)
    context = {

        'jobs': jobs,
        'savedjobs': savedjobs,
        'appliedjobs':appliedjobs,
        'total_applicants': total_applicants
    }

    return render(request, 'jobapp/dashboard.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def delete_job_view(request, id):

    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Your Job Post was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def make_complete_job_view(request, id):
    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:
        try:
            job.is_closed = True
            job.save()
            messages.success(request, 'Your Job was marked closed!')
        except:
            messages.success(request, 'Something went wrong !')
            
    return redirect('jobapp:dashboard')



@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def all_applicants_view(request, id):

    all_applicants = Applicant.objects.filter(job=id)

    context = {

        'all_applicants': all_applicants
    }

    return render(request, 'jobapp/all-applicants.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def delete_bookmark_view(request, id):

    job = get_object_or_404(BookmarkJob, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Saved Job was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def applicant_details_view(request, id):

    applicant = get_object_or_404(User, id=id)

    context = {

        'applicant': applicant
    }

    return render(request, 'jobapp/applicant-details.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def job_bookmark_view(request, id):

    form = JobBookmarkForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = BookmarkJob.objects.filter(user=request.user.id, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                messages.success(
                    request, 'You have successfully save this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:
        messages.error(request, 'You already saved this Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def job_edit_view(request, id=id):
    """
    Handle Employee Profile Update

    """

    job = get_object_or_404(Job, id=id)
    categories = Category.objects.all()
    form = JobEditForm(request.POST or None, instance=job)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # for save tags
        # form.save_m2m()
        messages.success(request, 'Your Job Post Was Successfully Updated!')
        return redirect(reverse("jobapp:single-job", kwargs={
            'id': instance.id
        }))
    context = {

        'form': form,
        'categories': categories
    }

    return render(request, 'jobapp/job-edit.html', context)
