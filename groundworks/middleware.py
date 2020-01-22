from django.conf import settings
from django.core.mail import mail_admins
from django.middleware.common import BrokenLinkEmailsMiddleware


class BrokenLinkEmailsToAdminsMiddleware(BrokenLinkEmailsMiddleware):
    """
    Exactly like its ancestor, but emails `settings.ADMINS` instead of
    `settings.MANAGERS`.
    """

    def process_response(self, request, response):
        """
        Send broken link emails for relevant 404 NOT FOUND responses to
        `settings.ADMINS`.
        """
        if response.status_code == 404 and not settings.DEBUG:
            domain = request.get_host()
            path = request.get_full_path()
            referer = force_text(request.META.get('HTTP_REFERER', ''), errors='replace')

            if not self.is_ignorable_request(request, path, domain, referer):
                ua = force_text(request.META.get('HTTP_USER_AGENT', '<none>'), errors='replace')
                ip = request.META.get('REMOTE_ADDR', '<none>')
                mail_admins(
                    "Broken %slink on %s" % (
                        ('INTERNAL ' if self.is_internal_request(domain, referer) else ''),
                        domain
                    ),
                    "Referrer: %s\nRequested URL: %s\nUser agent: %s\n"
                    "IP address: %s\n" % (referer, path, ua, ip),
                    fail_silently=True)
        return response
