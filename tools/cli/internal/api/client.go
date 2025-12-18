package api

import (
	"net/http"
	"time"
)

const DefaultBaseURL = "https://meal.servais-devos.com"

type Client struct {
	BaseURL string
	Client  *http.Client
}

func NewClient() *Client {
	return &Client{
		BaseURL: DefaultBaseURL,
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}
