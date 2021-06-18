from django.db import migrations
from messenger_backend.models import app_user, Conversations, Messages


def seed():
    print("db synced!")
    app_user.objects.all().delete()
    Conversations.objects.all().delete()
    Messages.objects.all().delete()

    thomas= app_user(
        username = "thomas",
        email =  "thomas@email.com",
        password=  "123456",
        photoUrl=  "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914467/messenger/thomas_kwzerk.png",
    )
        
    thomas.save()

    santiago= app_user(
        username= "santiago",
        email= "santiago@email.com",
        password= "123456",
        photoUrl="https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914466/messenger/775db5e79c5294846949f1f55059b53317f51e30_s3back.png",   
    )
    
    santiago.save()

    santiagoConvo= Conversations(
        user1Id= thomas,
        user2Id = santiago
    )
    santiagoConvo.save()

    messages= Messages(
        conversationId=santiagoConvo,
        senderId= santiago.id,
        text= "Where are you from?"
    )
    messages.save()

    messages= Messages(
        conversationId=santiagoConvo,
        senderId= thomas.id,
        text= "I'm from New York"
    )
    messages.save()

    messages= Messages(
        conversationId=santiagoConvo,
        senderId= santiago.id,
        text= "Share photo of your city, please"
    )
    messages.save()

    chiumbo= app_user(
        username= "chiumbo",
        email= "chiumbo@email.com",
        password= "123456",
        photoUrl=
        "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914468/messenger/8bc2e13b8ab74765fd57f0880f318eed1c3fb001_fownwt.png",
    )
    chiumbo.save()

    chiumboConvo= Conversations(
        user1Id= chiumbo,
        user2Id= thomas
    )
    chiumboConvo.save()

    messages= Messages(
        conversationId=chiumboConvo,
        senderId= chiumbo.id,
        text= "Sure! What time?"
    )
    messages.save()

    hualing= app_user(
        username= "hualing",
        email= "hualing@email.com",
        password= "123456",
        photoUrl=
        "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914466/messenger/6c4faa7d65bc24221c3d369a8889928158daede4_vk5tyg.png",
    )
    hualing.save()

    hualingConvo = Conversations(
        user1Id= hualing,
        user2Id= thomas
    )
    hualingConvo.save()

    for i in range(10):
        messages= Messages(
            conversationId=hualingConvo,
            senderId= hualing.id,
            text= "a test Messages"
        )
        messages.save()

    messages= Messages(
            conversationId=hualingConvo,
            senderId= hualing.id,
            text= "😂 😂 😂"
        )
    messages.save()

    user=app_user(
      username= "ashanti",
      email= "ashanti@email.com",
      password= "123456",
      photoUrl=
        "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914466/messenger/68f55f7799df6c8078a874cfe0a61a5e6e9e1687_e3kxp2.png",
    )
    user.save()

    user=app_user(
      username= "julia",

      email= "julia@email.com",
      password= "123456",
      photoUrl=
        "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914468/messenger/d9fc84a0d1d545d77e78aaad39c20c11d3355074_ed5gvz.png",
    )
    user.save()

    user=app_user(
      username= "cheng",
      email= "cheng@email.com",
      password= "123456",
      photoUrl=
        "https://res.cloudinary.com/dmlvthmqr/image/upload/v1607914466/messenger/9e2972c07afac45a8b03f5be3d0a796abe2e566e_ttq23y.png",
    )
    user.save()

    print('seeded users and Messagess')

print("Seeding...")
# class Migration(migrations.Migration):

#     dependencies = []

#     operations = [
#         migrations.RunPython(seed)
#     ]

    