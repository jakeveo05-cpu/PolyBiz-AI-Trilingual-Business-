/**
 * Google Drive Integration for PolyBiz Learning Stage
 * Allows users to sync their vocabulary lists and progress
 */

// Google API configuration
const SCOPES = "https://www.googleapis.com/auth/drive.file";
const DISCOVERY_DOC = "https://www.googleapis.com/discovery/v1/apis/drive/v3/rest";

// File names in Google Drive
const FILES = {
  VOCAB_LIST: "polybiz_vocab_list.csv",
  PROGRESS: "polybiz_progress.json",
  BACKUP: "polybiz_backup.json",
};

interface GoogleDriveFile {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime: string;
}

class GoogleDriveSync {
  private tokenClient: any = null;
  private gapiInited = false;
  private gisInited = false;
  private accessToken: string | null = null;

  /**
   * Initialize Google API client
   * Call this once when the app loads
   */
  async init(clientId: string, apiKey: string): Promise<boolean> {
    if (typeof window === "undefined") return false;

    try {
      // Load GAPI
      await this.loadScript("https://apis.google.com/js/api.js");
      await new Promise<void>((resolve) => {
        (window as any).gapi.load("client", resolve);
      });

      await (window as any).gapi.client.init({
        apiKey,
        discoveryDocs: [DISCOVERY_DOC],
      });
      this.gapiInited = true;

      // Load GIS (Google Identity Services)
      await this.loadScript("https://accounts.google.com/gsi/client");
      this.tokenClient = (window as any).google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: SCOPES,
        callback: (response: any) => {
          if (response.access_token) {
            this.accessToken = response.access_token;
          }
        },
      });
      this.gisInited = true;

      return true;
    } catch (error) {
      console.error("Google Drive init error:", error);
      return false;
    }
  }

  private loadScript(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }
      const script = document.createElement("script");
      script.src = src;
      script.onload = () => resolve();
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  /**
   * Request user authorization
   */
  async authorize(): Promise<boolean> {
    if (!this.gisInited || !this.tokenClient) {
      throw new Error("Google Drive not initialized");
    }

    return new Promise((resolve) => {
      this.tokenClient.callback = (response: any) => {
        if (response.access_token) {
          this.accessToken = response.access_token;
          resolve(true);
        } else {
          resolve(false);
        }
      };
      this.tokenClient.requestAccessToken({ prompt: "consent" });
    });
  }

  /**
   * Check if user is authorized
   */
  isAuthorized(): boolean {
    return !!this.accessToken;
  }

  /**
   * Sign out
   */
  signOut(): void {
    if (this.accessToken) {
      (window as any).google.accounts.oauth2.revoke(this.accessToken);
      this.accessToken = null;
    }
  }

  /**
   * Find a file by name in Google Drive
   */
  private async findFile(fileName: string): Promise<GoogleDriveFile | null> {
    if (!this.accessToken) return null;

    try {
      const response = await (window as any).gapi.client.drive.files.list({
        q: `name='${fileName}' and trashed=false`,
        fields: "files(id, name, mimeType, modifiedTime)",
        spaces: "drive",
      });

      const files = response.result.files;
      return files && files.length > 0 ? files[0] : null;
    } catch (error) {
      console.error("Find file error:", error);
      return null;
    }
  }

  /**
   * Upload or update a file
   */
  async uploadFile(fileName: string, content: string, mimeType = "text/plain"): Promise<string | null> {
    if (!this.accessToken) {
      throw new Error("Not authorized");
    }

    try {
      const existingFile = await this.findFile(fileName);
      const metadata = {
        name: fileName,
        mimeType,
      };

      const form = new FormData();
      form.append(
        "metadata",
        new Blob([JSON.stringify(metadata)], { type: "application/json" })
      );
      form.append("file", new Blob([content], { type: mimeType }));

      const url = existingFile
        ? `https://www.googleapis.com/upload/drive/v3/files/${existingFile.id}?uploadType=multipart`
        : "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart";

      const response = await fetch(url, {
        method: existingFile ? "PATCH" : "POST",
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
        body: form,
      });

      const result = await response.json();
      return result.id || null;
    } catch (error) {
      console.error("Upload file error:", error);
      return null;
    }
  }

  /**
   * Download a file's content
   */
  async downloadFile(fileName: string): Promise<string | null> {
    if (!this.accessToken) {
      throw new Error("Not authorized");
    }

    try {
      const file = await this.findFile(fileName);
      if (!file) return null;

      const response = await fetch(
        `https://www.googleapis.com/drive/v3/files/${file.id}?alt=media`,
        {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
          },
        }
      );

      return await response.text();
    } catch (error) {
      console.error("Download file error:", error);
      return null;
    }
  }

  /**
   * Sync vocabulary list to Google Drive (CSV format)
   */
  async syncVocabList(vocabCSV: string): Promise<boolean> {
    const fileId = await this.uploadFile(FILES.VOCAB_LIST, vocabCSV, "text/csv");
    return !!fileId;
  }

  /**
   * Download vocabulary list from Google Drive
   */
  async downloadVocabList(): Promise<string | null> {
    return this.downloadFile(FILES.VOCAB_LIST);
  }

  /**
   * Backup all progress to Google Drive
   */
  async backupProgress(progressJSON: string): Promise<boolean> {
    const fileId = await this.uploadFile(FILES.BACKUP, progressJSON, "application/json");
    return !!fileId;
  }

  /**
   * Restore progress from Google Drive
   */
  async restoreProgress(): Promise<string | null> {
    return this.downloadFile(FILES.BACKUP);
  }

  /**
   * Get last sync time
   */
  async getLastSyncTime(): Promise<Date | null> {
    const file = await this.findFile(FILES.BACKUP);
    return file ? new Date(file.modifiedTime) : null;
  }
}

// Singleton instance
export const googleDrive = new GoogleDriveSync();

// React hook for Google Drive sync
export function useGoogleDriveSync() {
  // This would be implemented with React hooks
  // For now, export the class methods
  return {
    init: googleDrive.init.bind(googleDrive),
    authorize: googleDrive.authorize.bind(googleDrive),
    isAuthorized: googleDrive.isAuthorized.bind(googleDrive),
    signOut: googleDrive.signOut.bind(googleDrive),
    syncVocabList: googleDrive.syncVocabList.bind(googleDrive),
    downloadVocabList: googleDrive.downloadVocabList.bind(googleDrive),
    backupProgress: googleDrive.backupProgress.bind(googleDrive),
    restoreProgress: googleDrive.restoreProgress.bind(googleDrive),
    getLastSyncTime: googleDrive.getLastSyncTime.bind(googleDrive),
  };
}
