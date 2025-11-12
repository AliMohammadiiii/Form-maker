"""
Script to assign a form to a user
Usage: python assign_form.py <form_uuid> <username>
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from forms.models import Form

def assign_form_to_user(form_uuid, username):
    try:
        # Get the form
        form = Form.objects.get(uuid=form_uuid)
        
        # Get the user
        user = User.objects.get(username=username)
        
        # Assign the form to the user
        form.created_by = user
        form.save()
        
        print(f"✅ Successfully assigned form '{form.title}' (UUID: {form_uuid}) to user '{username}'")
        return True
    except Form.DoesNotExist:
        print(f"❌ Error: Form with UUID '{form_uuid}' not found")
        return False
    except User.DoesNotExist:
        print(f"❌ Error: User with username '{username}' not found")
        print(f"Available users: {', '.join(User.objects.values_list('username', flat=True))}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python assign_form.py <form_uuid> <username>")
        print("Example: python assign_form.py b4f1d0be-2392-493b-aa52-1be66b4e503c ali")
        sys.exit(1)
    
    form_uuid = sys.argv[1]
    username = sys.argv[2]
    
    assign_form_to_user(form_uuid, username)




