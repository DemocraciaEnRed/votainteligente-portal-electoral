# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test import override_settings
from django.core import mail
from elections.models import Election, Candidate
from preguntales.models import (Message,
                                Answer,
                                MessageStatus,
                                MessageConfirmation,
                                OutboundMessage,
                                Attachment
                                )
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from mock import patch, call
from preguntales.forms import MessageForm
from preguntales.tasks import send_mails
from django.template import Context
from django.template.loader import get_template
from unittest import skip
from django.core.files import File
from preguntales.tests import __testing_mails__, __attachrments_dir__
import os

THE_CURRENT_MEDIA_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/testing_mails/attachments'

EMAIL_LOCALPART='municipales2016'
EMAIL_DOMAIN='votainteligente.cl'

@override_settings(EMAIL_DOMAIN=EMAIL_DOMAIN,
                   EMAIL_LOCALPART=EMAIL_LOCALPART)
class MessageTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_instanciate_a_message(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         )

        self.assertIsNone(message.accepted)
        self.assertFalse(message.sent)
        self.assertIsNone(message.confirmed)
        self.assertTrue(message.slug)
        self.assertIn(message.slug, 'perrito')
        self.assertIsInstance(message.created,datetime)
        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='Perrito',
                                          content='content',
                                          )
        self.assertNotEquals(message.slug, message2.slug)

    def test_str(self):
        message = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        expected_unicode = 'author preguntó "subject" en 2a Circunscripcion Antofagasta'
        self.assertEquals(message.__str__(), expected_unicode)

    def test_a_message_has_a_message_detail_url(self):
        message = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        url = reverse('message_detail',kwargs={'election_slug':self.election.slug, 'pk':message.id})
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('election', response.context)
        self.assertIn('votainteligentemessage', response.context)
        self.assertEquals(response.context['election'], self.election)
        self.assertEquals(response.context['votainteligentemessage'], message)
        self.assertTemplateUsed(response, 'elections/message_detail.html')
        site = Site.objects.get_current()
        self.assertEquals("http://%s%s"%(site.domain,url), message.get_absolute_url())

    def test_accept_message(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertFalse(message.accepted)

        # Now I moderate this
        # which means I send an email with a confirmation email
        #
        message.accept_moderation()

        self.assertFalse(message.sent)
        self.assertTrue(message.accepted)

    def test_send_mail(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertEquals(len(mail.outbox), 0)
        message.send()
        self.assertEquals(len(mail.outbox), 2)
        the_mail = mail.outbox[0]
        self.assertIn(the_mail.to[0], [self.candidate1.email, self.candidate2.email])
        context = Context({'election': self.election,
                           'candidate': self.candidate1,
                           'message': message
                          })
        template_body = get_template('mails/nueva_pregunta_candidato_body.html')
        expected_content= template_body.render(context)
        self.assertEquals(the_mail.body, expected_content)
        template_subject = get_template('mails/nueva_pregunta_candidato_subject.html')
        expected_subject = template_subject.render(context).replace('\n', '').replace('\r', '')
        self.assertEquals(the_mail.subject, expected_subject)
        message = Message.objects.get(id=message.id)
        self.assertTrue(message.sent)
        self.assertTrue(message.outbound_identifiers.all())
        self.assertTrue(message.outbound_identifiers.filter(person=self.candidate1))
        self.assertTrue(message.outbound_identifiers.filter(person=self.candidate2))
        identifiers = message.outbound_identifiers.all()
        # reply-to part
        reply_to_arrays = []
        for identifier in identifiers:
            reply_to_arrays.append('%(localpart)s+%(key)s@%(domain)s' % {'localpart': EMAIL_LOCALPART,
                                                                  'domain': EMAIL_DOMAIN,
                                                                  'key':identifier.key})
        for the_mail in mail.outbox:
            self.assertEquals(len(the_mail.reply_to), 1)
            self.assertIn(the_mail.reply_to[0], reply_to_arrays)

    def test_the_class_has_a_function_that_will_send_mails(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified',
                                          accepted=True
                                          )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified'
                                          )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)

        self.assertEquals(len(mail.outbox), 0)
        Message.send_mails()
        sent_mails = Message.objects.filter(status__sent=True)
        self.assertEquals(len(sent_mails), 2)
        self.assertTrue(Message.objects.get(id=message.id).sent)
        self.assertTrue(Message.objects.get(id=message2.id).sent)
        self.assertEquals(len(mail.outbox), 4)

    def test_messages_listing_needing_moderation_messages(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified',
                                          accepted=True
                                          )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified'
                                          )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)

        messages = Message.objects.needing_moderation_messages()

        self.assertIn(message3, messages)
        self.assertEquals(len(messages), 1)


    def test_reject_message(self):
        message = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertIsNone(message.accepted)

        message.reject_moderation()
        #the message has been moderated
        self.assertFalse(message.accepted)

class MessageOutboundIdentifier(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='Perrito',
                                              content='content',
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)

    def test_instantiate(self):
        outbound = OutboundMessage.objects.create(message=self.message, person=self.candidate1)
        self.assertTrue(outbound)
        self.assertIn(outbound, self.message.outbound_identifiers.all())
        self.assertTrue(outbound.key)
        self.assertIsInstance(outbound.key, str)
        self.assertNotIn('-', outbound.key)

    def test_no_two_equal_keys(self):
        outbound1 = OutboundMessage.objects.create(message=self.message, person=self.candidate1)
        outbound2 = OutboundMessage.objects.create(message=self.message, person=self.candidate1)
        self.assertNotEqual(outbound1.key, outbound2.key)


class AnswerAttachmentTestCase(TestCase):
    def setUp(self):
        super(AnswerAttachmentTestCase, self).setUp()
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='Perrito',
                                              content='content',
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)
        self.answer = Answer.objects.create(message=self.message,
                                            person=self.candidate1,
                                            content='This is a content')
        self.pdf_file = File(open(__attachrments_dir__ + "hello.pd.pdf", 'rb'))
        self.photo_fiera = File(open(__attachrments_dir__ + "fiera_parque.jpg", 'rb'))

    @override_settings(MEDIA_ROOT=THE_CURRENT_MEDIA_ROOT)
    def test_instantiate(self):
        attachment = Attachment.objects.create(answer=self.answer,
                                               content=self.photo_fiera,
                                               name="foto-fiera.jpg"
                                               )
        self.assertTrue(attachment)

class MessageStatusTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='Perrito',
                                              content='content',
                                              )

    def test_instanciate(self):
        ## Deleting things before creating anything
        MessageStatus.objects.all().delete()
        status = MessageStatus.objects.create(message=self.message)
        self.assertIsNone(status.accepted)
        self.assertFalse(status.sent)
        self.assertIsNone(status.confirmed)
        self.assertEquals(status.message, self.message)

    def test_automatically_create_status(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         )
        self.assertTrue(message.status)

    def test_passing_variables_to_status(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         accepted=True
                                         )
        self.assertTrue(message.status.accepted)


@override_settings(NO_REPLY_MAIL="no-reply@votainteligente.cl")
class ConfirmationTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='subject',
                                              content='content',
                                              slug='subject-slugified',
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)

    def test_instanciate(self):
        confirmation = MessageConfirmation.objects.create(message=self.message)
        self.assertTrue(confirmation.key)
        self.assertIsNone(confirmation.when_confirmed)
        self.assertTrue(confirmation.created)
        self.assertTrue(confirmation.updated)

    def test_message_create_confirmation(self):
        self.message.create_confirmation()
        self.assertTrue(self.message.confirmation)
        self.assertEquals(len(mail.outbox), 1)
        context = Context({'election': self.election, 'message': self.message})
        template_subject = get_template('mails/confirmation_subject.html')
        template_body = get_template('mails/confirmation_body.html')
        expected_subject = template_subject.render(context)
        expected_body = template_body.render(context)
        the_mail = mail.outbox[0]
        self.assertIn(self.message.author_email, the_mail.to)
        self.assertEquals("no-reply@votainteligente.cl", the_mail.from_email)

    def test_confirm_message(self):
        self.message.create_confirmation()
        self.message.confirm()
        self.assertTrue(self.message.confirmation.when_confirmed)
        self.assertTrue(self.message.confirmed)
        ## Deleting confirmation
        self.message.confirmation.delete()
        ## Creating a new one
        self.message.create_confirmation()
        url = reverse('confirmation', kwargs={'key': self.message.confirmation.key})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('preguntales/confirmation.html')
        self.assertEquals(response.context['message'], self.message)
        self.message = Message.objects.get(id=self.message.id)
        self.assertTrue(self.message.confirmation.when_confirmed)
        self.assertTrue(self.message.confirmed)
        #I cannot get the same address again
        self.assertEquals(self.client.get(url).status_code, 404)

    def test_confirmation_url(self):
        self.message.create_confirmation()
        confirmation = self.message.confirmation
        url = confirmation.get_absolute_url()
        response = self.client.get(url)
        self.message = Message.objects.get(id=self.message.id)
        self.assertTrue(self.message.confirmed)


class AnswerTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='subject',
                                              content='content',
                                              slug='subject-slugified',
                                              accepted=True
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)

    def test_create_an_answer(self):
        answer = Answer.objects.create(
            content=u'Hey I\'ve had to speak english in the last couple of days',
            message=self.message,
            person=self.candidate1
            )

        self.assertTrue(answer)
        self.assertEquals(answer.content, u'Hey I\'ve had to speak english in the last couple of days')
        self.assertEquals(answer.message, self.message)
        self.assertEquals(answer.person, self.candidate1)
        self.assertIsNotNone(answer.created)
        self.assertIsInstance(answer.created, datetime)

        self.assertIn(answer, self.message.answers.all())
        self.assertIn(answer, self.candidate1.answers.all())


class MessagesOrderedList(TestCase):
    def setUp(self):
        super(MessagesOrderedList, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

        self.message1 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'I\'m moderated',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message2 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'message 3',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message3 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'please don\'t moderate me',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified'
                                                              )
        self.message4 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'message 4',
                                                              content=u'Que opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message4.people.add(self.candidate1)

        self.answer1 = Answer.objects.create(message=self.message4,
                                             person=self.candidate1,
                                             content=u'answerto message4'
                                             )
        self.message5 = Message.objects.create(election=self.election,
                                               author_name='author',
                                               author_email='author email',
                                               subject=u'message 5',
                                               content=u'Que opina usted sobre el test_accept_message',
                                               slug='subject-slugified',
                                               accepted=True
                                               )


    def test_message_class_has_a_manager(self):
        messages = Message.ordered.all()

        self.assertEquals(messages.count(), 5)
        self.assertEquals(messages[0], self.message4)#because it has answers
        self.assertEquals(messages[1], self.message5)#because it was the last created
        self.assertEquals(messages[2], self.message2)#the third should not appear here because it has not been moderated
        self.assertEquals(messages[3], self.message1)
        self.assertEquals(messages[4], self.message3)#this hasn't been moderated


class PreguntalesWebTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def tearDown(self):
        pass

    def test_get_the_url(self):
        url = reverse('ask_detail_view',
            kwargs={
            'slug':self.election.slug
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('election', response.context)
        self.assertEquals(response.context['election'], self.election)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], MessageForm)
        self.assertIn('messages', response.context)
        self.assertTemplateUsed(response, 'elections/ask_candidate.html')

    def test_submit_message(self):
        url = reverse('ask_detail_view', kwargs={'slug':self.election.slug,})
        self.candidate1.email = "email@email.com"
        self.candidate1.save()
        self.candidate2.email = "email@email.com"
        self.candidate2.save()
        response = self.client.post(url, {'people': [self.candidate1.pk, self.candidate2.pk],
                                            'subject': 'this important issue',
                                            'content': 'this is a very important message',
                                            'author_name': 'my name',
                                            'author_email': 'mail@mail.er',
                                            # 'recaptcha_response_field': 'PASSED'
                                            }, follow=True
                                            )

        self.assertTemplateUsed(response, 'elections/ask_candidate.html')
        self.assertEquals(Message.objects.count(), 1)
        new_message = Message.objects.all()[0]
        self.assertFalse(new_message.sent)
        self.assertFalse(new_message.accepted)
        self.assertEquals(new_message.content, 'this is a very important message')
        self.assertEquals(new_message.subject, 'this important issue')
        self.assertEquals(new_message.people.all().count(), 2)

    def test_persons_belongs_to_instance_and_is_reachable(self):
        message_form = MessageForm(election=self.election)

        alejandro_guille = Candidate.objects.get(name='Alejandro Guillier')
        alejandro_guille.email = 'eduardo@guillier.cl'
        alejandro_guille.save()

        election_candidates = self.election.candidates.exclude(email__isnull=True).exclude(email="")

        self.assertQuerysetEqual(election_candidates,
                                 [repr(r) for r in message_form.fields['people'].queryset],
                                 ordered=False)

    def test_form_creates_confirmation(self):
        data = {'people': [self.candidate1.pk, self.candidate2.pk],
                'subject': 'this important issue',
                'content': 'this is a very important message',
                'author_name': 'my name',
                'author_email': 'mail@mail.er',
                }
        message_form = MessageForm(data, election=self.election)
        print message_form.errors
        self.assertTrue(message_form.is_valid())
        message = message_form.save()
        self.assertTrue(message.confirmation)


class MessageSenderTestCase(TestCase):
    '''
    This TestCase is intended to provide testing for the periodically
    push VotaInteligente Messages to WriteIt (writeit.ciudadanointeligente.org).
    '''
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_push_moderated_messages(self):
        '''Push moderated messages'''
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)
        message.status.accepted = True
        message.status.save()

        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified',
                                          )
        message2.status.accepted = True
        message2.status.save()
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)
        send_mails.delay()
        self.assertEquals(Message.objects.filter(status__sent=True).count(), 2)
        self.assertIn(message, Message.objects.filter(status__sent=True))
        self.assertIn(message2, Message.objects.filter(status__sent=True))
        self.assertEquals(len(mail.outbox), 4)
