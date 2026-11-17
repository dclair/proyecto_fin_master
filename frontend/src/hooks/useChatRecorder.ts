/**
 * Custom Hook for Voice Recording using standard MediaRecorder API
 * Encapsulates audio streams, chunking, timer, and cleanup.
 */
import { useState, useRef, useEffect, useCallback } from 'react';

interface UseChatRecorderOptions {
  onRecorded: (audioFile: File) => void;
  onError?: (err: unknown) => void;
}

export interface UseChatRecorderResult {
  isRecording: boolean;
  recordingTime: number;
  formattedTime: string;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  cancelRecording: () => void;
}

export const useChatRecorder = ({ onRecorded, onError }: UseChatRecorderOptions): UseChatRecorderResult => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null);

  // Formatear segundos en mm:ss
  const formatTime = (seconds: number): string => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const cleanupTimer = useCallback(() => {
    if (timerIntervalRef.current !== null) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  }, []);

  const cleanupTracks = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        cleanupTracks();
        cleanupTimer();

        if (audioChunksRef.current.length === 0) return;

        const mime = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mime });
        const ext = mime.includes('mp4') ? 'mp4' : 'webm';
        const file = new File([audioBlob], `voice_message_${Date.now()}.${ext}`, {
          type: mime,
        });

        setIsRecording(false);
        setRecordingTime(0);
        onRecorded(file);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerIntervalRef.current = window.setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('[useChatRecorder]: Error al acceder al micrófono:', err);
      if (onError) {
        onError(err);
      } else {
        alert('No se pudo acceder al micrófono. Por favor, verifica los permisos.');
      }
    }
  }, [cleanupTimer, cleanupTracks, onRecorded, onError]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  }, [isRecording]);

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.onstop = null; // Evitar disparar onRecorded
      mediaRecorderRef.current.stop();
      cleanupTracks();
      cleanupTimer();
      setIsRecording(false);
      setRecordingTime(0);
      audioChunksRef.current = [];
    }
  }, [isRecording, cleanupTracks, cleanupTimer]);

  useEffect(() => {
    return () => {
      cleanupTimer();
      cleanupTracks();
    };
  }, [cleanupTimer, cleanupTracks]);

  return {
    isRecording,
    recordingTime,
    formattedTime: formatTime(recordingTime),
    startRecording,
    stopRecording,
    cancelRecording,
  };
};

export default useChatRecorder;
