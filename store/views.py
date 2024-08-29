from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect

from django.urls import reverse,reverse_lazy

from store.forms import SignUpForm,SignInForm,UserProfileForm,ProjectForm

from django.views.generic import View,TemplateView,UpdateView,CreateView,DetailView

from django.contrib.auth import authenticate,login

from store.models import UserProfile,Project,WishListItems

class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=SignUpForm()

        return render(request,"store/signup.html",{"form":form_instance})

    def post(self,request,*args,**kwrags):

        form_instance=SignUpForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("signin")
        
        return render(request,"store/signup.html",{"form":form_instance})
        
    
    
class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=SignInForm()

        return render(request,"store/login.html",{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        form_instance=SignInForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            user_obj=authenticate(request,**data)

            if user_obj:

                login(request,user_obj)

                return redirect("index")
            
        return render(request,"store/login.html",{"form":form_instance})



KEY_SECRET="key_secret"

KEY_ID="key_id"



class IndexView(View):

    template_name="store/index.html"

    def get(self,request,*args,**kwargs):

        qs=Project.objects.all().exclude(owner=request.user)

        return render(request,self.template_name,{"projects":qs})
    


  
class UserProfileUpdateView(UpdateView):

    model=UserProfile

    form_class=UserProfileForm

    template_name="store/profile_edit.html"

    success_url=reverse_lazy("index")

    

    # def get_success_url(self):

    #     return reverse("index")


   
    
    


    # def get(self,request,*args,**kwargs):

    #     id=kwargs.get("pk")

    #     profile_obj=UserProfile.objects.get(id=id)

    #     form_instance=UserProfileForm(instance=profile_obj)

    #     return render(request,"store/profile_edit.html",{"form":form_instance})    




class ProjectCreateView(CreateView):

    model=Project

    form_class=ProjectForm

    template_name="store/project_add.html"

    success_url=reverse_lazy("index")

    
    def form_valid(self,form):

        form.instance.owner=self.request.user

        return super().form_valid(form)
    
class MyProjectListView(View):

    def get(self,request,*args,**kwargs):

        # qs=Project.objects.filter(owner=request.user)

        qs=request.user.projects.all()

        return render(request,"store/myprojects.html",{"works":qs})
    

class ProjectDeleteView(View):


    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Project.objects.get(id=id).delete()

        return redirect("myworks")

class ProjectDetailView(DetailView):

    template_name="store/project_detail.html"

    context_object_name="project"

    model=Project

class AddToWishLoistView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_obj=Project.objects.get(id=id)

        WishListItems.objects.create(
                                 wishlist_object= request.user.basket,
                                 project_object=project_obj

                                    )
        
        return redirect("index")

from django.db.models import Sum

class MyCartView(View):


    def get(self,request,*args,**kwargs):

        qs=request.user.basket.basket_items.filter(is_order_placed=False)

        total=request.user.basket.wishlist_total
        
        print(total)
        return render(request,"store/wishlist_summary.html",{"cartitems":qs,"total":total})




class WishListItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        WishListItems.objects.get(id=id).delete()

       

        return redirect("my-cart")

        
import razorpay

class ChekOutView(View):

    def get(self,request,*args,**kwargs):

        client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

        amount=request.user.basket.wishlist_total*100       

        data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }

        payment = client.order.create(data=data)

        print(payment)

        return render(request,"store/payment.html")






