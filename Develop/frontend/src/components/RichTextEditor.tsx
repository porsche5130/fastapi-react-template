import React from 'react';
import { LexicalComposer } from '@lexical/react/LexicalComposer';
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin';
import { ContentEditable } from '@lexical/react/LexicalContentEditable';
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin';
import { AutoFocusPlugin } from '@lexical/react/LexicalAutoFocusPlugin';
import { LexicalErrorBoundary } from '@lexical/react/LexicalErrorBoundary';
import { HeadingNode, QuoteNode } from '@lexical/rich-text';
import { ListItemNode, ListNode } from '@lexical/list';
import { LinkNode } from '@lexical/link';
import { ListPlugin } from '@lexical/react/LexicalListPlugin';
import { LinkPlugin } from '@lexical/react/LexicalLinkPlugin';
import ToolbarPlugin from './ToolbarPlugin';
import { $generateHtmlFromNodes, $generateNodesFromDOM } from '@lexical/html';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import { $getRoot, $insertNodes } from 'lexical';
import '../styles/RichTextEditor.css';

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

// Plugin to set initial HTML content
function InitialContentPlugin({ html }: { html: string }) {
  const [editor] = useLexicalComposerContext();
  const [isFirstRender, setIsFirstRender] = React.useState(true);

  React.useEffect(() => {
    if (html && isFirstRender) {
      editor.update(() => {
        const parser = new DOMParser();
        const dom = parser.parseFromString(html, 'text/html');
        const nodes = $generateNodesFromDOM(editor, dom);
        const root = $getRoot();
        root.clear();
        root.select();
        $insertNodes(nodes);
      });
      setIsFirstRender(false);
    }
  }, [editor, html, isFirstRender]);

  return null;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  disabled = false,
  placeholder = '請輸入內容...'
}) => {
  const initialConfig = {
    namespace: 'RichTextEditor',
    theme: {
      paragraph: 'editor-paragraph',
      heading: {
        h1: 'editor-heading-h1',
        h2: 'editor-heading-h2',
        h3: 'editor-heading-h3',
      },
      list: {
        ul: 'editor-list-ul',
        ol: 'editor-list-ol',
      },
      link: 'editor-link',
    },
    onError: (error: Error) => {
      console.error('Lexical error:', error);
    },
    nodes: [
      HeadingNode,
      QuoteNode,
      ListNode,
      ListItemNode,
      LinkNode,
    ],
    editable: !disabled,
  };

  // OnChange handler component
  function OnChangeHandler() {
    const [editor] = useLexicalComposerContext();

    React.useEffect(() => {
      return editor.registerUpdateListener(({ editorState }) => {
        editorState.read(() => {
          const htmlString = $generateHtmlFromNodes(editor);
          onChange(htmlString);
        });
      });
    }, [editor]);

    return null;
  }

  return (
    <div className={`rich-text-editor ${disabled ? 'disabled' : ''}`}>
      <LexicalComposer initialConfig={initialConfig}>
        {!disabled && <ToolbarPlugin />}
        <div className="editor-container">
          <RichTextPlugin
            contentEditable={
              <ContentEditable
                className="editor-input"
                style={{ minHeight: '300px' }}
              />
            }
            placeholder={
              <div className="editor-placeholder">{placeholder}</div>
            }
            ErrorBoundary={LexicalErrorBoundary}
          />
          <HistoryPlugin />
          <AutoFocusPlugin />
          <ListPlugin />
          <LinkPlugin />
          <OnChangeHandler />
          <InitialContentPlugin html={value} />
        </div>
      </LexicalComposer>
    </div>
  );
};

export default RichTextEditor;
