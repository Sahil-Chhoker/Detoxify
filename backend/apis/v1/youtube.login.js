// apis/v1/youtube.login.js
class YouTubeLoginHandler {
    constructor(userId) {
        this.userId = userId;
        // Update WebSocket URL to match your FastAPI endpoint
        this.ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/youtube-login/${userId}`);
        this.setupWebSocket();
    }

    async initialize() {
        try {
            // Check for existing session
            const response = await fetch(`/api/v1/youtube/session/${this.userId}`);
            if (response.ok) {
                const sessionData = await response.json();
                return true;
            }
        } catch (error) {
            console.error('No existing session found:', error);
        }

        // No valid session found, start new login flow
        return this.startYouTubeLogin();
    }

    setupWebSocket() {
        this.ws.onopen = () => {
            console.log('WebSocket connection established');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received:', data);
            
            if (data.type === 'session_stored') {
                console.log('YouTube session stored successfully');
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
        };
    }

    async startYouTubeLogin() {
        const consent = await this.getUserConsent();
        if (!consent) return false;

        const popup = window.open('https://accounts.google.com/signin/v2/identifier?service=youtube', 
            'YouTube Login', 
            'width=800,height=600');

        return new Promise((resolve) => {
            const checkLogin = setInterval(async () => {
                try {
                    const authData = await this.getYouTubeAuthData(popup);
                    if (authData) {
                        this.ws.send(JSON.stringify({
                            type: 'youtube_session',
                            authData: authData,
                            userAgent: navigator.userAgent
                        }));
                        
                        clearInterval(checkLogin);
                        popup.close();
                        resolve(true);
                    }
                } catch (e) {
                    console.error('Error checking login:', e);
                    if (popup.closed) {
                        clearInterval(checkLogin);
                        resolve(false);
                    }
                }
            }, 1000);
        });
    }

    getUserConsent() {
        return confirm(
            'Would you like to save your YouTube login state? ' +
            'This will allow you to stay logged in for future sessions. ' +
            'You can revoke this permission at any time.'
        );
    }

    async logout() {
        this.ws.send(JSON.stringify({ type: 'logout' }));
    }
}

// Export for use in other parts of your application
export default YouTubeLoginHandler;