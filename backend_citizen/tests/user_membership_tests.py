# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.models import Organization, Enrollment
from backend_citizen.forms import OrganizationForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import vcr


PASSWORD = 'perrito'


class CitizenMembershipTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CitizenMembershipTestCase, self).setUp()
        self.org = Organization.objects.create(name="Local Organization")
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(PASSWORD)
        self.fiera.save()

    def test_relating_a_user_and_an_organization(self):
        membership = Enrollment.objects.create(user=self.feli,
                                               organization=self.org)
        self.assertTrue(membership.created)
        self.assertTrue(membership.updated)
        self.assertIn(membership, self.feli.enrollments.all())
        self.assertIn(membership, self.org.enrollments.all())

    @vcr.use_cassette('fixtures/vcr_cassettes/circoroto.yaml')
    def test_creating_an_organization_form(self):
        data = {'name': 'Circo Roto',
                'facebook_page': 'https://www.facebook.com/circoroto/?fref=ts'
                }
        form = OrganizationForm(data=data,
                                user=self.feli)
        self.assertTrue(form.is_valid())
        organization = form.save()
        self.assertEquals(organization.name, data['name'])
        self.assertIsInstance(organization, Organization)
        self.assertTrue(organization.enrollments.all())
        enrollment = organization.enrollments.first()
        self.assertEquals(enrollment.user, self.feli)
        self.assertEquals(organization.description, u'Agrupación de circo del barrio Yungay')
        self.assertTrue(organization.images.all())

    @vcr.use_cassette('fixtures/vcr_cassettes/circoroto.yaml')
    def test_creating_an_organization_view(self):
        url = reverse('backend_citizen:create_organization')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login')+"?next="+url)
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], OrganizationForm)
        self.assertEquals(response.context['form'].user, self.fiera)
        self.assertTemplateUsed(response, 'backend_citizen/create_organization.html')
        data = {'name': 'Circo Roto',
                'facebook_page': 'https://www.facebook.com/circoroto/?fref=ts'
                }
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertTemplateUsed(response, 'popular_proposal/organization.html')
        self.assertTrue(response.context['organization'])
        organization = response.context['organization']
        self.assertEquals(organization.name, u'Circo Roto')
