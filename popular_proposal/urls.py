from django.conf.urls import url
from popular_proposal.views.proposal_views import (SubscriptionView,
                                                   HomeView,
                                                   PopularProposalDetailView,
                                                   PopularProposalUpdateView,
                                                   UnlikeProposalView,
                                                   CommitmentDetailView,
                                                   PopularProposalOGImageView,
                                                   PopularProposalDetailRedirectView,
                                                   PopularProposalAyuranosView,
                                                   )
from popular_proposal.views.wizard import (ProposalWizard,
                                           ProposalWizardFull,
                                           ProposalWizardFullWithoutArea,)
from django.views.decorators.clickjacking import xframe_options_exempt


urlpatterns = [
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^embedded/?$',
        xframe_options_exempt(HomeView.as_view(is_embedded=True)),
        name='embedded_home'),
    url(r'^create_wizard/(?P<slug>[-\w]+)/?$',
        ProposalWizard.as_view(),
        name='propose_wizard'),
    ## This depends on area
    url(r'^create_wizard_full/?$',
        ProposalWizardFull.as_view(),
        name='propose_wizard_full'),
    ## this depends on area
    url(r'^crear/?$',
        ProposalWizardFullWithoutArea.as_view(),
        name='propose_wizard_full_without_area'),
    url(r'^detail/(?P<slug>[-\w]+)/?$',
        xframe_options_exempt(PopularProposalDetailView.as_view()),
        name='detail'),
    url(r'^ayudanos/(?P<slug>[-\w]+)/?$',
        PopularProposalAyuranosView.as_view(),
        name='ayuranos'),
    url(r'^d/(?P<pk>\d+)/?$',
        PopularProposalDetailRedirectView.as_view(),
        name='short_detail'),
    url(r'^og_image/(?P<slug>[-\w]+).jpg$',
        PopularProposalOGImageView.as_view(),
        name='og_image'),
    url(r'^commitment/(?P<authority_slug>[-\w]+)/(?P<proposal_slug>[-\w]+)/?$',
        CommitmentDetailView.as_view(),
        name='commitment'),
    url(r'^embedded_detail/(?P<slug>[-\w]+)/?$',
        xframe_options_exempt(PopularProposalDetailView.as_view(is_embedded=True)),
        name='embedded_detail'),
    url(r'^unlike/(?P<pk>\d+)/?$',
        UnlikeProposalView.as_view(),
        name='unlike_proposal'),
    url(r'^actualizar/(?P<slug>[-\w]+)/?$',
        PopularProposalUpdateView.as_view(),
        name='citizen_update'),
    url(r'^(?P<pk>[-\w]+)/subscribe/?$',
        SubscriptionView.as_view(),
        name='like_a_proposal'),
]
