package api

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// Recipe represents the data returned by meal.servais-devos.com
type Recipe struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	// Add other fields as they appear in your API JSON
}

// GetRecipes fetches the list from the API
func (c *Client) GetRecipes() ([]Recipe, error) {
	// 1. Build the URL
	url := fmt.Sprintf("%s/recipes?skip=0&limit=20", c.BaseURL) // Adjust path as needed

	// 2. Make the request
	resp, err := c.Client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status: %d", resp.StatusCode)
	}

	// 3. Decode the JSON
	var recipes []Recipe
	if err := json.NewDecoder(resp.Body).Decode(&recipes); err != nil {
		return nil, err
	}

	return recipes, nil
}
