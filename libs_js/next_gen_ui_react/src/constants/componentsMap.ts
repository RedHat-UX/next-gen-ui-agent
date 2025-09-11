import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@patternfly/react-core";

import AccordionWrapper from "../components/AccordionWrapper";
import { CodeBlockWrapper } from "../components/CodeBloackWrapper";
import CustomLink from "../components/CustomLink";
import ListWrapper from "../components/ListWrapper";
import Message from "../components/Message";
import OneCardWrapper from "../components/OneCardWrapper";
import QuickResponse from "../components/QuickResponse";
import TableWrapper from "../components/TableWrapper";
import Text from "../components/Text";
import VideoPlayerWrapper from "../components/VideoPlayerWrapper";

export const componentsMap = {
  accordion: AccordionWrapper,
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
  message: Message,
  "one-card": OneCardWrapper,
  quickResponse: QuickResponse,
  table: TableWrapper,
  "video-player": VideoPlayerWrapper,
};
