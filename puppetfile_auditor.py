#!/usr/bin/env python

"""
Detects if puppet modules in Puppetfile contain the tag information
and prints out those not using tags convention

Example Standalone Usage:

    $ python puppetfile_auditor.py
    External repos that's not using tag:
    https://github.com/thias/puppet-postfix
    https://github.com/hercules-team/augeasproviders_core.git
    https://github.com/tobyriddell/puppet-conrep.git
    https://github.com/jtopjian/puppet-reprepro.git
    https://github.com/unibet/puppet-profiled.git
    https://github.com/hercules-team/augeasproviders_pam.git
    https://github.com/rodjek/puppet-logrotate.git
    https://github.com/puppetlabs/puppetlabs-java_ks.git
    https://github.com/hercules-team/augeasproviders_ssh.git
    https://github.com/hercules-team/augeasproviders_sysctl.git
    https://github.com/ringingliberty/puppet-chrony.git
    https://github.com/camptocamp/puppet-kmod.git
    https://github.com/puppetlabs/puppetlabs-ntp.git
    https://github.com/puppetlabs/puppetlabs-rabbitmq.git

    Internal repos that's not using tag:
    git@gitlab.company.com:puppet/varnish.git
    git@gitlab.company.com:puppet/systemd.git

"""

import re
from collections import Counter
import requests
import time


gitlab_api_url = "https://gitlab.company.com/api/v3"
gitlab_token = "put your private gitlab api token here"
group_id = 123
github_api_url = "https://api.github.com"
github_token = "put your private github api token here"
puppetfile = "../foreman-puppetfile/Puppetfile"

def get_puppetfile_tags(puppetfile):
    """
    obtain tags from Puppetfile
    :return: tuple(list, list)
    """
    regex_vcs = re.compile(r"^:(git|svn)\s+=>\s+['\"](.+)['\"]\,", re.I)
    regex_tag = re.compile(r"^:(ref|tag|commit|branch)\s+=>\s+['\"](.+)['\"]\,?", re.I)

    vcss = []
    tags = []
    with open(puppetfile) as f:
        for line in f:
            match_vcs = regex_vcs.match(line.strip())
            if match_vcs:
                vcss.append(match_vcs.group(2))

            match_tag = regex_tag.match(line.strip())
            if match_tag:
                tags.append(match_tag.group(2))

    if len(vcss) == len(tags):
        return vcss, tags


def get_gitlab_tags(proj_id):
    """
    obtain tags from Gitlab
    :param proj_id: project id in Gitlab
    :return: list
    """
    result = []
    r = requests.get("{}/projects/{}/repository/tags".format(gitlab_api_url, proj_id),
                     headers={"PRIVATE-TOKEN": gitlab_token})
    if r.status_code == requests.codes.ok:
        for tag in r.json():
            result.append(tag['name'])
    return result


def get_github_bad_tags(puppetfile):
    """
    :param puppetfile:
    :return: list of 'bad' (not using tag) github urls
    """
    regex_github = re.compile(r"^:(?:git|svn)\s+=>\s+['\"]https://github.com/(.+)/(.+)(?:.git)?['\"]\,?", re.I)
    vcss_p, tags_p = get_puppetfile_tags(puppetfile=puppetfile)
    vcss_tags_p = zip(vcss_p, tags_p)
    bad = []
    with open(puppetfile) as f:
        for line in f:
            match_github = regex_github.match(line.strip())
            if match_github:
                owner, repo = match_github.group(1), re.sub('\.git$', '', match_github.group(2))
                r = requests.get("{}/repos/{}/{}/tags".format(github_api_url, owner, repo),
                                 headers={"Authorization": "token {}".format(github_token)})
                # in case reaches github api limit increase this value
                time.sleep(0.5)
                if r.status_code == requests.codes.ok:
                    for vcs_p, tag_p in vcss_tags_p:
                        if all(stuff in vcs_p for stuff in [owner, repo, 'github']):
                            for tag in r.json():
                                if tag_p == tag['name']:
                                    break
                            else:
                                bad.append(vcs_p)
    return list(set(bad))


def get_gitlab_bad_tags():
    """
    obtain a list of repos that uses things other than tag
    :return:
    """
    r = requests.get("{}/groups/{}".format(gitlab_api_url, group_id),
                     headers={"PRIVATE-TOKEN": gitlab_token})
    if r.status_code == requests.codes.ok:
        vcss, tags = get_puppetfile_tags(puppetfile=puppetfile)
        if (vcss, tags):
            return [project['ssh_url_to_repo']
                    for project in r.json()['projects']
                    for vcs, tag in zip(vcss, tags)
                    if vcs in (project['http_url_to_repo'], project['ssh_url_to_repo'])
                    and (tag not in get_gitlab_tags(project['id']))]


def print_bad():
    print "External repos that's not using tag:"
    for bad in get_github_bad_tags(puppetfile=puppetfile):
        print bad

    print

    print "Internal repos that's not using tag:"
    for bad in get_gitlab_bad_tags():
        print bad

if __name__ == "__main__":

    print_bad()

