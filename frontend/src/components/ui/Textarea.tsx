
import React from 'react';

const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>((props, ref) => {
  return (
    <textarea
      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      ref={ref}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';

export default Textarea;
