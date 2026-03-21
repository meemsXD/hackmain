from django.utils import timezone

def has_driver_access_to_batch(user, batch):
    if not user.is_authenticated:
        return False
    return batch.driver_grants.filter(driver=user, expires_at__gt=timezone.now()).exists()
