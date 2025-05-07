import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  CardTitle,
  List,
  ListItem,
  Text,
} from "@patternfly/react-core";

import {
  AccordionItemWrapper,
  AccordionWrapper,
} from "../components/AccordionWrapper";
import { CodeBlockWrapper } from "../components/CodeBloackWrapper";
import CustomLink from "../components/CustomLink";
import ListWrapper from "../components/ListWrapper";
import MarkdownWrapper from "../components/MarkdownWrapper";
import Message from "../components/Message";
import QuickResponse from "../components/QuickResponse";
import TableWrapper from "../components/TableWrapper";

export const componentsMap = {
  accordion: AccordionWrapper,
  accordionItem: AccordionItemWrapper,
  card: Card,
  cardHeader: CardHeader,
  cardTitle: CardTitle,
  cardBody: CardBody,
  cardFooter: CardFooter,
  codeblock: CodeBlockWrapper,
  text: Text,
  button: Button,
  list: ListWrapper,
  link: CustomLink,
  quickResponse: QuickResponse,
  table: TableWrapper,
  message: Message,
  markdown: MarkdownWrapper,
};
