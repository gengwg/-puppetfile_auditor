Detects if puppet modules in Puppetfile contain the tag information
and prints out those not using tags convention.
Useful for auditting puppet repos.
Can audit both github (external) and gitlab (internal).

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


