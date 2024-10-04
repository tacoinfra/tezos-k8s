"use strict";(self.webpackChunkdocusaurus=self.webpackChunkdocusaurus||[]).push([[952],{8566:(e,n,o)=>{o.r(n),o.d(n,{assets:()=>a,contentTitle:()=>r,default:()=>u,frontMatter:()=>i,metadata:()=>l,toc:()=>c});var s=o(5893),t=o(1151);const i={},r="Public network node",l={id:"Public-Node",title:"Public network node",description:"Connecting to a public net is easy!",source:"@site/Public-Node.md",sourceDirName:".",slug:"/Public-Node",permalink:"/Public-Node",draft:!1,unlisted:!1,tags:[],version:"current",frontMatter:{},sidebar:"tezosK8sSidebar",previous:{title:"Prerequisites",permalink:"/Prerequisites"},next:{title:"Tezos Baker",permalink:"/Baker"}},a={},c=[];function d(e){const n={a:"a",code:"code",h1:"h1",li:"li",p:"p",pre:"pre",ul:"ul",...(0,t.a)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(n.h1,{id:"public-network-node",children:"Public network node"}),"\n",(0,s.jsx)(n.p,{children:"Connecting to a public net is easy!"}),"\n",(0,s.jsxs)(n.p,{children:["(See ",(0,s.jsx)(n.a,{href:"https://tezos.gitlab.io/user/history_modes.html",children:"here"})," for info on snapshots and node history modes)"]}),"\n",(0,s.jsx)(n.p,{children:"Simply run the following to spin up a rolling history node:"}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-shell",children:"helm install tezos-mainnet tacoinfra/tezos-chain \\\n--namespace tacoinfra --create-namespace\n"})}),"\n",(0,s.jsx)(n.p,{children:"Running this results in:"}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["Creating a Helm ",(0,s.jsx)(n.a,{href:"https://helm.sh/docs/intro/using_helm/#three-big-concepts",children:"release"})," named tezos-mainnet for your k8s cluster."]}),"\n",(0,s.jsx)(n.li,{children:"k8s will spin up one regular (i.e. non-baking node) which will download and import a mainnet snapshot. This will take a few minutes."}),"\n",(0,s.jsx)(n.li,{children:"Once the snapshot step is done, your node will be bootstrapped and syncing with mainnet!"}),"\n"]}),"\n",(0,s.jsxs)(n.p,{children:["You can find your node in the tacoinfra namespace with some status information using ",(0,s.jsx)(n.code,{children:"kubectl"}),"."]}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-shell",children:"kubectl -n tacoinfra get pods -l appType=octez-node\n"})}),"\n",(0,s.jsxs)(n.p,{children:["You can monitor (and follow using the ",(0,s.jsx)(n.code,{children:"-f"})," flag) the logs of the snapshot downloader/import container:"]}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-shell",children:"kubectl logs -n tacoinfra statefulset/rolling-node -c snapshot-downloader -f\n"})}),"\n",(0,s.jsx)(n.p,{children:"You can view logs for your node using the following command:"}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-shell",children:"kubectl -n tacoinfra logs -l appType=octez-node -c octez-node -f --prefix\n"})})]})}function u(e={}){const{wrapper:n}={...(0,t.a)(),...e.components};return n?(0,s.jsx)(n,{...e,children:(0,s.jsx)(d,{...e})}):d(e)}},1151:(e,n,o)=>{o.d(n,{Z:()=>l,a:()=>r});var s=o(7294);const t={},i=s.createContext(t);function r(e){const n=s.useContext(i);return s.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(t):e.components||t:r(e.components),s.createElement(i.Provider,{value:n},e.children)}}}]);