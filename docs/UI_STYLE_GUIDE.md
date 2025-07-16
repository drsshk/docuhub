# DocuHub UI Style Guide

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Layout System](#layout-system)
5. [Component Library](#component-library)
6. [Animation & Interactions](#animation--interactions)
7. [Responsive Design](#responsive-design)
8. [Accessibility Guidelines](#accessibility-guidelines)
9. [Code Examples](#code-examples)

## Design System Overview

DocuHub follows a modern, professional design system built on TailwindCSS with custom enhancements. The system emphasizes:

- **Clean, minimal aesthetics** with glassmorphism effects
- **Consistent spacing** using 4px/8px grid system
- **Semantic color usage** for status and actions
- **Smooth animations** with reduced motion support
- **Mobile-first responsive design**
- **Accessibility-compliant** interactions

## Color Palette

### Primary Colors
```css
:root {
    --primary-color: #2563eb;      /* Blue-600 */
    --secondary-color: #64748b;    /* Slate-500 */
    --success-color: #059669;      /* Emerald-600 */
    --warning-color: #d97706;      /* Amber-600 */
    --danger-color: #dc2626;       /* Red-600 */
}
```

### Status Colors
- **Approved**: `bg-green-100 text-green-800`
- **Pending**: `bg-yellow-100 text-yellow-800`
- **Draft**: `bg-gray-100 text-gray-800`
- **Rejected**: `bg-red-100 text-red-800`
- **Revise**: `bg-purple-100 text-purple-800`
- **Obsolete**: `bg-gray-100 text-gray-600`

### Dark Mode Colors
```css
:root {
    --dark-bg: #0f172a;          /* Slate-900 */
    --dark-surface: #1e293b;     /* Slate-800 */
    --dark-border: #334155;      /* Slate-700 */
}
```

### Dark Mode Implementation
DocuHub uses a sophisticated dark mode system that automatically adapts all components. The dark mode is toggled via JavaScript and persisted in localStorage.

#### HTML Root Class
```html
<html lang="en" class="h-full bg-gray-50 dark:bg-slate-900">
```

#### Dark Mode Toggle
```html
<button onclick="toggleDarkMode()" class="group relative text-blue-200 hover:text-white p-3 rounded-xl transition-all duration-300 hover:bg-white/10 backdrop-blur-sm" title="Toggle Dark Mode">
    <svg class="w-5 h-5 dark:hidden group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
    </svg>
    <svg class="w-5 h-5 hidden dark:block group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
    </svg>
</button>
```

## Typography

### Font Hierarchy
```css
/* Page Titles */
.page-title {
    @apply text-3xl font-bold text-gray-900 dark:text-white;
}

/* Section Headers */
.section-header {
    @apply text-lg font-medium text-gray-900 dark:text-white;
}

/* Body Text */
.body-text {
    @apply text-sm text-gray-700 dark:text-gray-300;
}

/* Meta Text */
.meta-text {
    @apply text-xs text-gray-500 dark:text-gray-400;
}

/* Links */
.link {
    @apply text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300;
}
```

### Font Sizes
- **XL**: `text-3xl` (30px) - Page titles
- **Large**: `text-lg` (18px) - Section headers
- **Base**: `text-sm` (14px) - Body text
- **Small**: `text-xs` (12px) - Meta information

## Layout System

### Container Patterns
```html
<!-- Page Container -->
<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
        <!-- Content -->
    </div>
</div>

<!-- Card Container -->
<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <!-- Card Content -->
</div>

<!-- Grid Layout -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Grid Items -->
</div>
```

### Spacing System
- **Micro**: `space-y-1` (4px)
- **Tight**: `space-y-2` (8px)
- **Compact**: `space-y-4` (16px)
- **Standard**: `space-y-6` (24px)
- **Comfortable**: `space-y-8` (32px)

## Component Library

### 1. Buttons

#### Primary Button
```html
<button class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 focus:bg-blue-700 active:bg-blue-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition ease-in-out duration-150">
    Primary Action
</button>
```

#### Secondary Button
```html
<button class="inline-flex items-center px-4 py-2 bg-gray-300 border border-transparent rounded-md font-semibold text-xs text-gray-700 uppercase tracking-widest hover:bg-gray-400 focus:bg-gray-400 active:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition ease-in-out duration-150">
    Secondary Action
</button>
```

#### Floating Action Button
```html
<button class="floating bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-full shadow-lg transition-all duration-300">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
    </svg>
</button>
```

### 2. Form Elements

#### Input Field
```html
<div>
    <label class="block text-sm font-medium text-gray-700 mb-2">
        Field Label <span class="text-red-500">*</span>
    </label>
    <input type="text" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
    <p class="mt-1 text-sm text-gray-500">Helper text for the field</p>
</div>
```

#### Textarea
```html
<textarea rows="4" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"></textarea>
```

#### Select Dropdown
```html
<select class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
    <option>Select an option</option>
</select>
```

### 3. Cards

#### Basic Card
```html
<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Card Title</h3>
    <p class="text-gray-600 dark:text-gray-300">Card content goes here.</p>
</div>
```

#### Dark Mode Card Variations
```html
<!-- Glass Card with Dark Mode -->
<div class="glass rounded-xl p-6 dark:bg-gray-800/95 dark:border-gray-700">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Glass Card</h3>
    <p class="text-gray-600 dark:text-gray-300">Glass morphism with dark mode support</p>
</div>

<!-- Dashboard Hero Card -->
<div class="glass rounded-2xl p-8 gradient-bg text-white dark:bg-gray-800/95 dark:border-gray-700">
    <h1 class="text-4xl font-bold">Welcome back!</h1>
    <p class="text-blue-100">Your project management command center</p>
</div>
```

#### Floating Card (with hover effect)
```html
<div class="floating bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
    <!-- Card content -->
</div>
```

#### Glass Morphism Card
```html
<div class="glass rounded-xl p-6">
    <!-- Card content with backdrop blur effect -->
</div>
```

### 4. Status Indicators

#### Status Pills
```html
<!-- Approved -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
    Approved
</span>

<!-- Pending -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
    Pending
</span>

<!-- Rejected -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
    Rejected
</span>
```

#### Status Dots
```html
<div class="flex items-center">
    <span class="status-dot bg-green-500"></span>
    <span class="text-sm text-gray-700">Active</span>
</div>
```

### 5. Navigation

#### Header Navigation
```html
<nav class="bg-gradient-to-r from-blue-800 via-blue-900 to-indigo-900 shadow-2xl backdrop-blur-lg border-b border-blue-700/50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <!-- Navigation content -->
        </div>
    </div>
</nav>
```

#### Breadcrumbs
```html
<nav class="flex" aria-label="Breadcrumb">
    <ol class="inline-flex items-center space-x-1 md:space-x-3">
        <li class="inline-flex items-center">
            <a href="#" class="text-gray-700 hover:text-gray-900">Home</a>
        </li>
        <li>
            <div class="flex items-center">
                <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                </svg>
                <span class="text-gray-500">Current Page</span>
            </div>
        </li>
    </ol>
</nav>
```

### 6. Tables

#### Compact Table
```html
<div class="overflow-x-auto">
    <table class="table-compact min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Header
                </th>
            </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    Data
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

#### Mobile Card Layout (Alternative to table)
```html
<div class="card-layout space-y-4">
    <div class="project-card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-start mb-2">
            <h3 class="font-medium text-gray-900 dark:text-white">Project Name</h3>
            <span class="status-approved">Approved</span>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-300">Project details...</p>
    </div>
</div>
```

### 7. Modals

#### Standard Modal
```html
<div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <!-- Modal content -->
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <!-- Modal actions -->
            </div>
        </div>
    </div>
</div>
```

## Animation & Interactions

### Animation Classes
```css
/* Fade In Animation */
.fade-in {
    animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Slide Up Animation */
.slide-up {
    animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Scale In Animation */
.scale-in {
    animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

/* Floating Hover Effect */
.floating {
    transform: translateY(0);
    transition: transform 0.3s ease;
}

.floating:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

### Smooth Scrolling
```css
html {
    scroll-behavior: smooth;
    scroll-padding-top: 2rem;
}

.smooth-scroll {
    scroll-behavior: smooth;
    transition: scroll 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

### Advanced Animations (from home.html)
```css
/* Seamless Section Transitions */
@keyframes smoothSlideInView {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes cascadeIn {
    from {
        opacity: 0;
        transform: translateY(30px) rotateX(10deg);
    }
    to {
        opacity: 1;
        transform: translateY(0) rotateX(0deg);
    }
}

@keyframes morphTransition {
    0% {
        opacity: 0;
        transform: translateY(60px) scale(0.9);
        filter: blur(3px);
    }
    50% {
        opacity: 0.7;
        transform: translateY(20px) scale(0.98);
        filter: blur(1px);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
        filter: blur(0px);
    }
}
```

## Responsive Design

### Breakpoints
- **Small (sm)**: 640px and up
- **Medium (md)**: 768px and up
- **Large (lg)**: 1024px and up
- **Extra Large (xl)**: 1280px and up

### Responsive Patterns
```html
<!-- Responsive Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Items automatically adjust based on screen size -->
</div>

<!-- Responsive Text -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
    Responsive Heading
</h1>

<!-- Responsive Spacing -->
<div class="p-4 md:p-6 lg:p-8">
    <!-- Padding increases with screen size -->
</div>
```

### Mobile Navigation Pattern
```html
<!-- Desktop Navigation (hidden on mobile) -->
<div class="hidden md:flex items-center space-x-4">
    <!-- Navigation items -->
</div>

<!-- Mobile Menu Button (hidden on desktop) -->
<div class="md:hidden">
    <button id="mobile-menu-button" class="p-3 rounded-xl">
        <!-- Hamburger icon -->
    </button>
</div>

<!-- Mobile Menu (hidden by default) -->
<div id="mobile-menu" class="md:hidden hidden">
    <!-- Mobile navigation items -->
</div>
```

## Accessibility Guidelines

### Focus States
```css
.focus-visible:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

button:focus-visible,
a:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}
```

### Screen Reader Support
```html
<!-- Screen Reader Only Text -->
<span class="sr-only">Screen reader only content</span>

<!-- Proper ARIA Labels -->
<button aria-label="Close modal" aria-expanded="false">
    <svg class="w-6 h-6" fill="none" stroke="currentColor">
        <!-- Icon SVG -->
    </svg>
</button>

<!-- Semantic HTML -->
<main role="main">
    <h1>Page Title</h1>
    <section aria-labelledby="section-title">
        <h2 id="section-title">Section Title</h2>
    </section>
</main>
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
    .glass {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #000;
    }
    
    .dark .glass {
        background: rgba(0, 0, 0, 0.95);
        border: 2px solid #fff;
    }
}
```

## Code Examples

### Complete Form Component
```html
<div class="bg-white shadow rounded-lg p-6">
    <form class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Project Name <span class="text-red-500">*</span>
            </label>
            <input type="text" 
                   class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                   placeholder="Enter project name">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Description
            </label>
            <textarea rows="4" 
                      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Project description"></textarea>
        </div>
        
        <div class="flex justify-end space-x-3">
            <button type="button" 
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                Cancel
            </button>
            <button type="submit" 
                    class="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700">
                Save Project
            </button>
        </div>
    </form>
</div>
```

### Dashboard Stats Card
```html
<div class="floating bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-gray-700">
    <div class="flex items-center justify-between">
        <div class="space-y-2">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Projects</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white">24</p>
            <div class="flex items-center space-x-1">
                <span class="text-green-500 text-sm font-medium">+12%</span>
                <span class="text-gray-500 text-xs">vs last month</span>
            </div>
        </div>
        <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
        </div>
    </div>
</div>
```

### Project Status Table Row
```html
<tr class="hover:bg-gray-50">
    <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm font-medium text-gray-900">Project Alpha</div>
        <div class="text-sm text-gray-500">PAL-2024-001</div>
    </td>
    <td class="px-6 py-4 whitespace-nowrap">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <span class="status-dot bg-green-500"></span>
            Approved
        </span>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        v1.2
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <div class="flex items-center space-x-2">
            <button class="icon-btn text-blue-600 hover:text-blue-900">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
            </button>
            <button class="icon-btn text-green-600 hover:text-green-900">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
            </button>
        </div>
    </td>
</tr>
```

---

## Dark Mode Implementation Guidelines

### Essential Dark Mode Classes

When implementing dark mode, always include these essential classes:

#### Text Colors
- **Primary text**: `text-gray-900 dark:text-white`
- **Secondary text**: `text-gray-600 dark:text-gray-300`
- **Muted text**: `text-gray-500 dark:text-gray-400`

#### Background Colors
- **Page background**: `bg-gray-50 dark:bg-slate-900`
- **Card backgrounds**: `bg-white dark:bg-gray-800`
- **Table headers**: `bg-gray-50 dark:bg-gray-700`

#### Border Colors
- **Standard borders**: `border-gray-200 dark:border-gray-700`
- **Dividers**: `divide-gray-200 dark:divide-gray-700`

#### Interactive States
- **Hover states**: `hover:bg-gray-50 dark:hover:bg-gray-700`
- **Focus states**: Already handled by `.focus-visible` class

### Dark Mode JavaScript Implementation
```javascript
// Dark mode toggle function
function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.classList.contains('dark');
    
    if (isDark) {
        html.classList.remove('dark');
        localStorage.setItem('darkMode', 'false');
    } else {
        html.classList.add('dark');
        localStorage.setItem('darkMode', 'true');
    }
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.documentElement.classList.add('dark');
    }
});
```

### Status Indicators with Dark Mode
```html
<!-- Project Status with complete dark mode support -->
<span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full 
    {% if project.status == 'Draft' %}bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300
    {% elif project.status == 'Pending_Approval' %}bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300
    {% elif project.status == 'Approved_and_Endorsed' %}bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300
    {% elif project.status == 'Conditional_Approval' %}bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300
    {% elif project.status == 'Request_for_Revision' %}bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300
    {% elif project.status == 'Rejected' %}bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300
    {% else %}bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300{% endif %}">
    {{ project.get_status_display }}
</span>
```

### Component-Specific Dark Mode Examples

#### Navigation Notification Icons
```html
<div class="flex items-center text-green-600 dark:text-green-400">
    <svg class="w-4 h-4 mr-2 status-indicator" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
    </svg>
    <span class="text-sm font-medium">Notifications Active</span>
</div>
```

#### Login Form with Dark Mode
```html
<div class="login-card rounded-2xl p-8 card-slide-in dark:bg-gray-800/95 dark:border-gray-700">
    <h3 class="text-2xl font-bold text-gray-800 text-center mb-8 dark:text-white">
        <i class="fas fa-sign-in-alt mr-2 text-purple-600"></i>
        Sign In
    </h3>
    <!-- Form content with dark mode classes -->
</div>
```

#### Glass Effect with Dark Mode
```css
.glass-effect {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.95);
}

.dark .glass-effect {
    background: rgba(31, 41, 55, 0.95); /* dark:bg-gray-800/95 */
    border-color: #4b5563; /* dark:border-gray-700 */
}
```

#### Button Dark Mode Variants
```html
<!-- Primary button with dark mode support -->
<a href="#" class="inline-flex items-center justify-center px-8 py-4 bg-white text-slate-800 font-semibold rounded-xl hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl focus-visible dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600">
    Get Started
    <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
    </svg>
</a>
```

### CSS Dark Mode Utilities
```css
/* Glass morphism dark mode */
.dark .glass {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(51, 65, 85, 0.3);
}

/* Dark mode body styles */
.dark body {
    background: var(--dark-bg);
    color: #f1f5f9;
}

/* Override specific background colors */
.dark .bg-white {
    background: var(--dark-surface) !important;
}

/* Text color overrides */
.dark .text-gray-900 {
    color: #f1f5f9 !important;
}

.dark .text-gray-600 {
    color: #94a3b8 !important;
}

/* Border color overrides */
.dark .border-gray-200 {
    border-color: var(--dark-border) !important;
}
```

### Best Practices for Dark Mode

1. **Always test both modes**: Ensure all components work in both light and dark modes
2. **Use semantic colors**: Prefer semantic color names over specific hex values
3. **Maintain contrast ratios**: Ensure accessibility standards are met in both modes
4. **Test with real content**: Dark mode can reveal layout issues not visible in light mode
5. **Preserve user preference**: Always save and restore the user's dark mode preference
6. **Consistent toggle placement**: Keep the dark mode toggle in a consistent, accessible location
7. **Gradual transitions**: Use smooth transitions when switching modes to avoid jarring changes

### Common Dark Mode Patterns

#### Page Headers
```html
<h1 class="text-3xl font-bold text-gray-900 dark:text-white">Page Title</h1>
<p class="mt-2 text-gray-600 dark:text-gray-400">Page description</p>
```

#### Form Labels
```html
<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    Field Label <span class="text-red-500">*</span>
</label>
```

#### Quick Stats Cards
```html
<div class="bg-white rounded-lg shadow p-6 dark:bg-gray-800">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Stats</h3>
    <div class="space-y-3">
        <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-400">Emails Today</span>
            <span class="text-sm font-medium text-gray-900 dark:text-white">{{ emails_today|default:0 }}</span>
        </div>
    </div>
</div>
```

## Implementation Notes

1. **Always use semantic HTML** for better accessibility
2. **Include ARIA labels** for interactive elements
3. **Test with keyboard navigation** to ensure accessibility
4. **Respect user preferences** for reduced motion and high contrast
5. **Use consistent spacing** following the 4px/8px grid system
6. **Implement proper focus states** for all interactive elements
7. **Test responsive design** across all breakpoints
8. **Optimize animations** for performance on lower-end devices
9. **Always implement dark mode classes** for new components
10. **Test both light and dark modes** thoroughly

This style guide provides a comprehensive foundation for maintaining design consistency across DocuHub. When creating new components or pages, reference these patterns to ensure visual and functional consistency with the existing design system, including proper dark mode support.