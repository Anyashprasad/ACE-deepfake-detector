import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 outline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-green disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0",
    {
        variants: {
            variant: {
                default: "bg-neon-green text-background shadow-sm hover:bg-neon-green/90 hover:shadow-lg hover:shadow-neon-green/20",
                destructive:
                    "bg-red-500 text-white shadow-sm shadow-black/5 hover:bg-red-600",
                outline:
                    "border border-neon-green/30 bg-transparent shadow-sm hover:bg-neon-green/10 hover:border-neon-green text-neon-green",
                secondary:
                    "bg-glass-bg text-foreground shadow-sm border border-glass-border hover:bg-glass-bg/80 backdrop-blur-sm",
                ghost: "hover:bg-neon-green/10 hover:text-neon-green",
                link: "text-neon-green underline-offset-4 hover:underline",
            },
            size: {
                default: "h-10 px-4 py-2",
                sm: "h-8 rounded-lg px-3 text-xs",
                lg: "h-12 rounded-lg px-8 text-base",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    },
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
    loading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, loading = false, children, ...props }, ref) => {
        const Comp = asChild ? Slot : "button"
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                disabled={loading || props.disabled}
                {...props}
            >
                {loading ? (
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        <span>{children || "Loading..."}</span>
                    </div>
                ) : (
                    children
                )}
            </Comp>
        )
    },
)
Button.displayName = "Button"

export { Button, buttonVariants }
