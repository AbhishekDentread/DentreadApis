from django.db import models

# Create your models here.
from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser,Group, Permission
from tinymce.models import HTMLField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    DeveloperName = models.CharField(max_length=50,null=True,blank=True)
    CompanyName = models.CharField(max_length=50,null=True,blank=True)
    MobileNumber = models.IntegerField(null=True,blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email


from django.db import models





class Organisation(models.Model):
    id = models.AutoField(primary_key=True)
    org_id = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(default=datetime.now())
    orgname = models.CharField(max_length=200)
    ctperson_name = models.CharField(blank=True, null=True, max_length=200)
    manager = models.CharField(blank=True, null=True, max_length=200)
    orgtype = models.CharField(max_length=200)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    gstin = models.ImageField(upload_to='static/gstFile/', blank=True, null=True)
    status = models.CharField(max_length=20)
    address = models.CharField(max_length=64, blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    offered_service = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(blank=True, max_length=50)
    state = models.CharField(blank=True, max_length=50)
    pincode = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=30)
    regby_email = models.EmailField(blank=True, null=True)
    regby_userid = models.IntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to='static/logo/', blank=True, null=True)
    pan = models.ImageField(upload_to='static/panCard/', blank=True, null=True)
    cin = models.ImageField(upload_to='static/cinNo/', blank=True, null=True)
    regFile = models.ImageField(upload_to='static/regFile/', blank=True, null=True)
    bankName = models.CharField(blank=True, max_length=30)
    accountNumber = models.IntegerField(blank=True, null=True)
    ifscCode = models.CharField(blank=True, max_length=30)
    customFile = models.ImageField(upload_to='static/cancelledCheque/', null=True)
    paymentOption = models.CharField(blank=True, null=True, max_length=100)
    topUp = models.IntegerField(blank=True, null=True)
    topUpAvailable = models.IntegerField(blank=True, null=True)
    preferredLab = models.CharField(null=True, blank=True, max_length=200)
    connectionDate = models.DateField(null=True, blank=True)
    pickup = models.CharField(blank=True, null=True, max_length=100)
    admin = models.IntegerField(blank=True, null=True)
    managerId = models.IntegerField(blank=True, null=True)
    subscription = models.CharField(null=True, blank=True, max_length=100, default="Dentread Basic")
    subscriptionId = models.IntegerField(null=True, blank=True, default=1)
    pickuplocation = models.CharField(blank=True, null=True, max_length=100)
    # invoice Dedicate
    invoiceMonth = models.IntegerField(null=True, blank=True, default=0)
    invoicePath = models.FileField(upload_to='static/orgInvoice/')
    lab_connection = models.CharField(null=True, blank=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'dent_organisation'

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.CharField(null=True, blank=True, max_length=200)
    models.CharField(null=True, blank=True, max_length=200)
    orgid=models.ForeignKey(Organisation, on_delete=models.CASCADE)
    parent_orgid = models.CharField(null=True, blank=True, max_length=200)
    locate = models.CharField(max_length=200)
    regby = models.CharField(max_length=200)
    rdate = models.DateField(default=date.today)
    name = models.CharField(max_length=200)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=6)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    address_1 = models.CharField(max_length=128, null=True, blank=True,)
    address_2 = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=5, default="000000")
    medih = models.CharField(max_length=800)
    refdoctor = models.CharField(max_length=50,blank=True, null=True)
    docid = models.IntegerField(blank=True, null=True)
    reffor = models.CharField(max_length=300)
    dcm_status = models.CharField(max_length=50, blank=True, null=True)
    refptid = models.IntegerField(blank=True, null=True)
    refpt_orgid=models.IntegerField(blank=True, null=True)
    reforgid = models.IntegerField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'dent_patient'



class Users(models.Model):
    id = models.AutoField(primary_key=True)
    propic = models.ImageField(upload_to='static/profilepic/')
    sign = models.ImageField(upload_to='static/sign/', blank=True, null=True)
    name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    usertype = models.CharField(max_length=200)
    email = models.EmailField()
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    orgid = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    parent_orgid = models.CharField(null=True, blank=True, max_length=200)
    department = models.CharField(max_length=20)
    status = models.CharField(max_length=800)
    cbcta = models.CharField(blank=True, null=True, max_length=20)
    cbctb = models.CharField(blank=True, null=True, max_length=20)
    opg = models.CharField(blank=True, null=True, max_length=20)
    dci = models.CharField(blank=True, null=True, max_length=20)
    edu = models.CharField(blank=True, null=True, max_length=20)
    spec = models.CharField(blank=True, null=True, max_length=20)
    reforgid=models.IntegerField(blank=True, null=True)
    last_login = models.DateField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    salutation = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dent_users'


class ServiceOrder(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(null=True, blank=True, max_length=200)
    date = models.DateField(default=date.today)
    pid = models.CharField(null=True, blank=True, max_length=200)
    repid = models.IntegerField(null=True, blank=True)
    orgid = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    parent_orgid = models.CharField(null=True, blank=True, max_length=200)
    locate = models.CharField(max_length=200)
    age = models.IntegerField()
    name = models.CharField(max_length=200)
    study = models.CharField(max_length=200)
    text = HTMLField()
    repby = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    remark = models.CharField(max_length=400)
    prescription = models.ImageField(upload_to='static/prescription/')
    repsdate = models.DateTimeField(null=True, blank=True)
    signby = models.CharField(max_length=200)
    badge = models.CharField(max_length=400)
    signurl = models.CharField(max_length=400)
    portal = models.CharField(max_length=50)
    mailstatus = models.CharField(null=True, blank=True, max_length=50)
    upload = models.CharField(null=True, blank=True, max_length=50)
    ON_processby = models.CharField(null=True, blank=True, max_length=50)
    refptid = models.IntegerField(blank=True, null=True)
    refpt_orgid = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    pt_email = models.EmailField(blank=True, null=True)
    pt_contact = models.IntegerField(blank=True, null=True)
    reg_by = models.CharField(null=True, blank=True, max_length=50)
    gender = models.CharField(null=True, blank=True, max_length=100)
    reforgid = models.IntegerField(blank=True, null=True)
    price = models.CharField(max_length=200, blank=True, null=True)
    discount = models.CharField(max_length=200, blank=True, null=True)
    payable = models.IntegerField(blank=True, null=True)
    paid = models.IntegerField(blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)
    mode = models.CharField(max_length=200, blank=True, null=True)
    sgst = models.IntegerField(default=0, blank=True, null=True)
    cgst = models.IntegerField(default=0, blank=True, null=True)
    igst = models.IntegerField(default=0, blank=True, null=True)
    reforgid = models.IntegerField(blank=True, null=True)
    refstudy = models.CharField(max_length=200, blank=True, null=True)
    ref_price = models.IntegerField(blank=True, null=True)
    ref_paid = models.CharField(max_length=200, blank=True, null=True)
    ref_balance = models.CharField(max_length=200, blank=True, null=True)
    ParentPatient = models.CharField(max_length=200, blank=True, null=True)
    ParentStudy = models.CharField(max_length=200, blank=True, null=True)
    StudyInstanceUID = models.CharField(max_length=200, blank=True, null=True)
    driveid = models.CharField(max_length=200, blank=True, null=True)
    drivelink = models.CharField(max_length=200, blank=True, null=True)
    patient_id = models.CharField(null=True, blank=True, max_length=100)
    created_by = models.CharField(null=True, blank=True, max_length=100)
    reviewed_by = models.CharField(null=True, blank=True, max_length=100)
    shipped_by = models.CharField(null=True, blank=True, max_length=100)

    # Payment Status
    tracking_id = models.CharField(null=True, blank=True, max_length=100)
    bank_ref_no = models.CharField(null=True, blank=True, max_length=255)
    order_status = models.CharField(null=True, blank=True, max_length=255)
    payment_mode = models.CharField(null=True, blank=True, max_length=255)
    card_name = models.CharField(null=True, blank=True, max_length=255)
    status_message = models.CharField(null=True, blank=True, max_length=255)
    trans_date = models.DateTimeField(null=True, blank=True)

    ORDERID = models.CharField(max_length=100, blank=True, null=True)
    TXNID = models.CharField(max_length=100, blank=True, null=True)
    TXNAMOUNT = models.CharField(max_length=100, blank=True, null=True)
    BANKTXNID = models.CharField(max_length=100, blank=True, null=True)
    TXNDATE = models.DateTimeField(blank=True, null=True)
    RESPMSG = models.CharField(max_length=100, blank=True, null=True)
    paymentStatus = models.CharField(max_length=100, blank=True, null=True)
    preferredData = models.CharField(max_length=100, default='digitalData')
    lineOrderPrice = models.IntegerField(null=True, blank=True)
    tooth_notation = models.CharField(null=True, blank=True, max_length=50, default='FDI')
    referTo = models.IntegerField(null=True, blank=True)
    # File Info
    file = models.CharField(max_length=100, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    objects = models.Manager()
    # NextDicom
    ParentPatient1 = models.CharField(max_length=200, blank=True, null=True)
    ParentStudy1 = models.CharField(max_length=200, blank=True, null=True)
    StudyInstanceUID1 = models.CharField(max_length=200, blank=True, null=True)
    upload1 = models.CharField(null=True, blank=True, max_length=50)
    file1 = models.CharField(max_length=100, null=True, blank=True)
    size1 = models.IntegerField(null=True, blank=True)
    fileStatus = models.CharField(max_length=100, null=True, blank=True)
    fileComment = models.CharField(max_length=100, null=True, blank=True)
    fileStatus1 = models.CharField(max_length=100, null=True, blank=True)
    fileComment1 = models.CharField(max_length=100, null=True, blank=True)
    instance = models.CharField(max_length=200, blank=True, null=True)
    Path = models.CharField(max_length=200, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='static/dicomThumb/', null=True, blank=True)
    # Shipments
    shp_order_id = models.IntegerField(blank=True, null=True)
    shipment_id = models.IntegerField(blank=True, null=True)
    shipTo = models.CharField(max_length=200, blank=True, null=True)
    shipBy = models.CharField(max_length=200, blank=True, null=True)
    ship_status = models.CharField(max_length=200, blank=True, null=True)
    ship_date = models.DateField(null=True, blank=True)
    requestForShipment = models.CharField(max_length=200, blank=True, null=True)
    shpDescription = models.TextField(blank=True, null=True)
    pickup_scheduled_date = models.DateTimeField(blank=True, null=True)
    awb_code = models.CharField(max_length=200, blank=True, null=True)
    courier_name = models.CharField(max_length=200, blank=True, null=True)

    # Order Deligate
    deligate_to = models.IntegerField(null=True, blank=True)
    order_type = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dent_serviceorder'


class IOSFile(models.Model):
    id = models.AutoField(primary_key=True)
    orgid = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    parent_orgid = models.CharField(null=True, blank=True, max_length=200)
    repid = models.IntegerField(null = True, blank = True)
    sodrid = models.IntegerField(null = True, blank = True)
    topid = models.IntegerField(null = True, blank = True)
    pid = models.IntegerField(null = True, blank = True)
    file = models.FileField(upload_to='IOSfiles/')
    size = models.IntegerField(null=True, blank=True)
    fileName = models.CharField(max_length=150, null = True, blank = True)
    fileStatus = models.CharField(max_length=100, null = True, blank = True)
    fileComment = models.CharField(max_length=100, null = True, blank = True)
    site = models.CharField(max_length=100, null = True, blank = True, default='Others')
    badge = models.CharField(max_length=400)
    re_upload = models.CharField(max_length=100, null = True, blank = True)
    download = models.CharField(max_length=100, null = True, blank = True)
    thumbnail = models.ImageField(upload_to='static/thumb/', null = True, blank = True)
    date = models.DateField(default = date.today)

    class Meta:
        managed = False
        db_table = 'dent_iosfile'

