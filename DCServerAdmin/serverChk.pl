#!/usr/bin/perl -w

# Dream Cup �T�[�o����v���O����(�N���`�F�b�N�p)

require '/home/two/gameServer/procserver.ini.pl';


open(DATA,">> $ACT_EXEC_FILE") || die "$ACT_EXEC_FILE open err.";
flock(DATA, 2);
print DATA "pid_check \n";
close(DATA);

