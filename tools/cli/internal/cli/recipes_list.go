package cli

import (
	"fmt"
	"os"

	"github.com/fservais/mymealplanner/tools/cli/internal/api"
	"github.com/spf13/cobra"
)

// recipesListCmd represents the list command
var recipesListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all available recipes",
	Run: func(cmd *cobra.Command, args []string) {
		client := api.NewClient()
		recipes, err := client.GetRecipes()
		if err != nil {
			fmt.Printf("Error fetching recipes: %v\n", err)
			os.Exit(1)
		}

		for _, recipe := range recipes {
			fmt.Printf("%d - %s\n", recipe.ID, recipe.Name)
		}
	},
}

func init() {
	// 2. Attach 'list' to 'recipes'
	// This makes "mymealplanner recipes list" valid
	recipesCmd.AddCommand(recipesListCmd)
}
