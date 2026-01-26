/**
 * Transaction Extend Dialog
 * 交易延長確認對話框
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Warning as WarningIcon } from '@mui/icons-material';

interface TransactionExtendDialogProps {
  open: boolean;
  remainingSeconds: number;
  onExtend: () => void;
  onCancel: () => void;
}

const TransactionExtendDialog: React.FC<TransactionExtendDialogProps> = ({
  open,
  remainingSeconds,
  onExtend,
  onCancel
}) => {
  const { t } = useTranslation();

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (minutes > 0) {
      return `${minutes} ${t('transaction.minutes')} ${secs} ${t('transaction.seconds')}`;
    }
    return `${secs} ${t('transaction.seconds')}`;
  };

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          {t('transaction.extendTitle', '交易時限即將到期')}
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body1" gutterBottom>
          {t('transaction.extendMessage', '您的交易時限即將到期。')}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          {t('transaction.remainingTime', '剩餘時間')}: <strong>{formatTime(remainingSeconds)}</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {t('transaction.extendQuestion', '是否延長交易等待時間 30 分鐘？')}
        </Typography>
        <Typography variant="body2" color="warning.main" sx={{ mt: 2 }}>
          {t('transaction.extendWarning', '如果不延長或未回應，交易將自動取消，需要重新進行。')}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} color="inherit">
          {t('transaction.cancel', '取消交易')}
        </Button>
        <Button onClick={onExtend} variant="contained" color="primary" autoFocus>
          {t('transaction.extend', '延長 30 分鐘')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransactionExtendDialog;
