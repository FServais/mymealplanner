package cli

import "github.com/spf13/cobra"

// recipesCmd represents the base command for all recipe actions
var recipesCmd = &cobra.Command{
	Use:   "recipes",
	Short: "Manage your recipes",
	Long:  `Parent command for creating, listing, and updating recipes.`,
	// We don't need a Run function here because this is just a container
}

func init() {
	// 1. Attach 'recipes' to the 'root' command
	// This makes "mymealplanner recipes" valid
	rootCmd.AddCommand(recipesCmd)
}
